import datetime

import mock
import mock
import pytest

import ia.quality.algo as algo
import tests.fakes as fakes


@pytest.fixture()
def jira_mock():
    m = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1")
    i2 = fakes.Issue("ISSUE-2")
    i3 = fakes.Issue("ISSUE-3")
    i4 = fakes.Issue("ISSUE-4")
    m.search_issues.return_value = [i1, i2, i3, i4]
    return m


def test_maintenance_trend(jira_mock):
    periods = algo.get_periods("2020-07-01", 7, 1)
    trend = algo.maintenance_trend(jira_mock, periods, ("DANSRE", "DANMR", "DANCOE"))
    assert len(trend) ==1


def test_get_periods():
    periods = algo.get_periods("2020-07-01", 14, 5)

    assert len(periods) == 5
    assert periods[4][0] == datetime.datetime(year=2020, month=6, day=17) # start
    assert periods[4][1] == datetime.datetime(year=2020, month=7, day=1)  # end (latest)
    assert periods[3][0] == datetime.datetime(year=2020, month=6, day=3)
    assert periods[3][1] == datetime.datetime(year=2020, month=6, day=17)
    assert periods[2][0] == datetime.datetime(year=2020, month=5, day=20)
    assert periods[2][1] == datetime.datetime(year=2020, month=6, day=3)
    assert periods[1][0] == datetime.datetime(year=2020, month=5, day=6)
    assert periods[1][1] == datetime.datetime(year=2020, month=5, day=20)
    assert periods[0][0] == datetime.datetime(year=2020, month=4, day=22)
    assert periods[0][1] == datetime.datetime(year=2020, month=5, day=6)  # end (earliest)