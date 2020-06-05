'''Project status calculator'''
from ia.jira import issue as ticket
from datetime import datetime
from ia.jira import links as issuelinks
import ia.viz.charts as charts
import datetime


def progress(jira_access, jql, status_done=('Done', 'Waiting for production')):
    all_issues = ticket.search_issues(jira_access, jql)
    c_all = len(all_issues)
    done_issues = [i for i in all_issues if i.fields.status.name in status_done]
    c_done = len(done_issues)
    percentage = round(c_done*100/c_all, 0) if c_all else 0
    return percentage, all_issues, done_issues
