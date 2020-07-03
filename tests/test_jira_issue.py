import mock
import pytest

import ia.common.jira.issue as j
import tests.fakes as fakes
from ia.common.jira import issue as j
from ia.common.jira.issue import issues_cache


@pytest.fixture()
def jira_mock():
    m = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1")
    i2 = fakes.Issue("ISSUE-2")
    i3 = fakes.Issue("ISSUE-3")
    i4 = fakes.Issue("ISSUE-4")
    m.search_issues.return_value = [i1, i2, i3, i4]
    return m

@pytest.fixture
def issue_mock():
    m = mock.MagicMock()
    type(m.fields.project).key = mock.PropertyMock(return_value="COE")
    type(m.fields).issuelinks = mock.PropertyMock(return_value=[
        fakes.IssueLink("inwardIssue", f"{m.fields.project.key}-1"),
        fakes.IssueLink("inwardIssue", f"{m.fields.project.key}-2"),
        fakes.IssueLink("inwardIssue", "EXT-1", "Blocks"),
        fakes.IssueLink("outwardIssue", "EXT-2"),
    ])
    return m

def test_get_issue_by_key():
    jira_mock = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1")
    jira_mock.search_issues.return_value = [i1]
    issue_cache = j.get_issue_by_key(jira_mock, "ISSUE-1")
    assert issue_cache.issue == i1


def test_search_issues(jira_mock):
    issues = j.search_issues(jira_mock, "jql")
    assert len(issues) == 4


def test_load_external_issues():
    issue_cache = mock.MagicMock()
    j.load_external_issues(issue_cache, 2, ("Done"))

    assert len(issue_cache._linked_issues) == 0


def test_issue_cache(jira_mock, issue_mock):
    ic = j.IssueCache(jira_mock, issue_mock)
    assert ic.jira_access
    assert ic.issue 
    assert ic.fields 
    assert ic.project 
    assert ic.key
    assert ic.linked_issues == {}
    assert ic.status
    assert ic.sprints == []
    assert ic.epic_name == None
