import datetime

from tinydb import Query, TinyDB

from ia.common.helpers import day_ts, to_dt, to_ts

__db = TinyDB("metrics.json")


def save(name, squad_name, independency, all_issues, all_with_dep):
    Metrics = Query()
    ts = day_ts()
    return __db.upsert(
        {
            "name": name,
            "squad": squad_name,
            "independence": independency,
            "all_issues": [i.key for i in all_issues],
            "all_with_dep": [i.key for i in all_with_dep],
            "timestamp": ts,
        },
        Metrics.timestamp == ts
        and Metrics.name == name
        and Metrics.Squad == squad_name,
    )


def select_in(dt_1, dt_2):
    Metrics = Query()

    # ts_1 = min(ts1, ts2)
    # ts_2 = max(ts1, ts2)

    def time_window(ts):
        dt = to_dt(ts)
        return dt >= dt_1 and dt <= dt_2

    tw = time_window

    found = __db.search(Metrics.timestamp.test(tw))
    return found


def read_independence_stats(name, squad_name):
    Metrics = Query()
    found = __db.search(Metrics.name == name and Metrics.squad == squad_name)
    return IndependenceMetrics(found) if len(found) else None


class IndependenceMetrics:
    def __init__(self, metrics):
        self._metrics = metrics
        m_hist = {}
        for f in metrics:
            f_ts = f.get("timestamp")
            m_hist[to_dt(f_ts).date()] = f
        self.__history = m_hist
        self.__date_index = sorted(self.__history.keys())

    def get_sorted_dates(self):
        return self.__date_index

    def get_values(self, dates):
        values = []
        for d in dates:
            values.append(self.__history[d])
        return values

    def get_latest(self):
        if len(self.__date_index) > 0:
            latest_day = self.__date_index[-1]
            return self.__history[latest_day]
        else:
            return {}

    def get_trend(self):
        return (
            0
            if len(self.__history) <= 1
            else self.__history[self.__date_index[-1]]["independence"]
            - self.__history[self.__date_index[-2]]["independence"]
        )

    def get_history(self):
        return self.__history

    latest = property(get_latest)
    trend = property(get_trend)
    history = property(get_history)


def merge(independence_metrics_list):
    total_metrics = []
    dates = set()
    for im in independence_metrics_list:
        dates = dates.union(im.get_sorted_dates())

    for d in sorted(list(dates)):
        all_issues_by_date = set()
        all_with_deps_by_date = set()
        for im in independence_metrics_list:
            m = im.history.get(d, {})
            if len(m) > 0:
                name = m.get("name", "__merged__")
                all_issues_by_date = all_issues_by_date.union(m.get("all_issues", []))
                all_with_deps_by_date = all_with_deps_by_date.union(
                    m.get("all_with_dep", [])
                )

        total_metrics.append(
            {
                "name": name,
                "squad": "Merged",
                "independence": round(
                    100 - len(all_with_deps_by_date) * 100 / len(all_issues_by_date)
                )
                if len(all_issues_by_date)
                else 0,
                "all_issues": all_issues_by_date,
                "all_with_dep": all_with_deps_by_date,
                "timestamp": to_ts(
                    datetime.datetime(year=d.year, month=d.month, day=d.day)
                ),
            }
        )
    return IndependenceMetrics(total_metrics)
