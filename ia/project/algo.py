"""Project status calculator"""
import ia.common.jira.issue as ticket
import ia.execution.algo as execution_algo


def progress(jira_access, epic_key, status_done=("Done", "Waiting for production")):
    jql = f'"Epic Link" = {epic_key}'
    return execution_algo.progress(jira_access, jql, status_done)


