"""Quality check algorithms"""
import datetime
from typing import Dict, List, Tuple

from jira import JIRA

import ia.common.jira.issue as jira_logs
import ia.execution.algo as exec

DAY_STRING_FORMAT = "%Y-%m-%d"


def maintenance_backlog(
    jira_access, project_keys, issuetype, status_done
):  # pragma: no cover
    JQL = f"project in {project_keys} and issuetype in ({issuetype}) and status not in ({status_done})"
    all_maintenance = jira_logs.search_issues(jira_access, JQL)
    return all_maintenance


def maintenance_trend(
    jira_access, periods, project_keys, issuetype=("Bug", "User Story Bug"),
):
    # create: project = DANMR and issuetype in (Bug, "User Story Bug") and createdDate >= "2020-05-15" and createdDate <= "2020-06-01"
    # resolved: project = DANMR and issuetype in (Bug, "User Story Bug") and resolutiondate  >= "2020-05-15" and resolutiondate  <= "2020-06-01"

    trend = []
    for p in periods:
        start_date = f"{p[0]:%Y-%m-%d}"
        end_date = f"{p[1]:%Y-%m-%d}"
        JQL_created = f'project in {project_keys} and issuetype in ({issuetype}) and createdDate >= "{start_date}" and createdDate <= "{end_date}"'
        JQL_resolved = f'project in {project_keys} and issuetype in ({issuetype}) and resolutiondate >= "{start_date}" and resolutiondate <= "{end_date}"'

        created_defects = jira_logs.search_issues(jira_access, JQL_created)
        resolved_defects = jira_logs.search_issues(jira_access, JQL_resolved)
        trend.append((created_defects, resolved_defects))

    return trend


def get_periods(
    period_end_day: str, period_days: int = 14, no_periods: int = 5
) -> List[Tuple[datetime.datetime, datetime.datetime]]:
    periods = []
    last_period_end_date = datetime.datetime.strptime(period_end_day, DAY_STRING_FORMAT)
    end_date = last_period_end_date

    for _ in enumerate(range(0, no_periods)):
        start_date = end_date - datetime.timedelta(days=period_days)
        periods.insert(0, (start_date, end_date))
        end_date = start_date
    return periods
