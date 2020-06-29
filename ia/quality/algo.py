"""Quality check algorithms"""
import datetime

from jira import JIRA

import ia.common.jira.issue as jira_logs


def maintenance_backlog(jira_access, project_key, issuetype, status_done):
    JQL = f"project = {project_key} and issuetype in ({issuetype}) and status not in ({status_done})"
    all_maintenance = jira_logs.search_issues(jira_access, JQL)
    return all_maintenance


def maintenance_trend(
    jira_access, project_key, start_date, end_date, issuetype=("Bug", "User Story Bug"),
):
    # create: project = DANMR and issuetype in (Bug, "User Story Bug") and createdDate >= "2020-05-15" and createdDate <= "2020-06-01"
    # resolved: project = DANMR and issuetype in (Bug, "User Story Bug") and resolutiondate  >= "2020-05-15" and resolutiondate  <= "2020-06-01"
    JQL_created = f'project = {project_key} and issuetype in ({issuetype}) and createdDate >= "{start_date}" and createdDate <= "{end_date}"'
    JQL_resolved = f'project = {project_key} and issuetype in ({issuetype}) and resolutiondate >= "{start_date}" and resolutiondate <= "{end_date}"'

    created_defects = jira_logs.search_issues(jira_access, JQL_created)
    resolved_defects = jira_logs.search_issues(jira_access, JQL_resolved)

    return created_defects, resolved_defects
