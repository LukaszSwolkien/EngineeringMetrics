import mock
import pytest

import ia.dependency.algo as dep
import tests.fakes as fakes


@pytest.fixture()
def jira_mock():
    m = mock.MagicMock()
    i1 = fakes.Issue('ISSUE-1')
    i2 = fakes.Issue('ISSUE-2')
    i3 = fakes.Issue('ISSUE-3')
    i4 = fakes.Issue('ISSUE-4')
    m.search_issues.return_value = [i1, i2, i3, i4]
    return m


def test_dependency_factor_0(jira_mock):
    p, all_issues, all_with_dep = dep.dependency_factor(jira_mock, "jql")
    assert p == 0
    assert all_with_dep == []
    assert len(all_issues) == 4


def test_external_links_20(jira_mock):
    i5 = fakes.Issue('ISSUE-5')
    i5.fields.issuelinks = [
        fakes.IssueLink('inwardIssue', 'Dep-1'), 
        fakes.IssueLink('inwardIssue', 'Dep-2'),
        fakes.IssueLink('outwardIssue', 'Dep-3')
    ]
    jira_mock.search_issues.return_value += [i5]
    p, all_issues, all_with_dep = dep.dependency_factor(jira_mock, "jql")
    assert p == 20
    assert len(all_with_dep) == 1
    assert all_with_dep[0].key == 'ISSUE-5'
    assert len(all_issues) == 5


def test_external_links_100(jira_mock): # issue-5 is dependent on
    i5 = fakes.Issue('ISSUE-5')
    i5.fields.issuelinks = [
        fakes.IssueLink('outwardIssue', 'Dep-1'), 
    ]
    jira_mock.search_issues.return_value = [i5]
    p, all_issues, all_with_dep  = dep.dependency_factor(jira_mock, "jql")
    assert p == 100
    assert len(all_with_dep) == 1
    assert all_with_dep[0].key == 'ISSUE-5'
    assert len(all_issues) == 1


def test_external_links_0(jira_mock): # issue-5 is a dependency for the other issue
    i5 = fakes.Issue('ISSUE-5')
    i5.fields.issuelinks = [
        fakes.IssueLink('inwardIssue', 'Dep-1'), 
    ]
    jira_mock.search_issues.return_value = [i5]
    p, all_issues, all_with_dep  = dep.dependency_factor(jira_mock, "jql")
    assert p == 0
    assert len(all_with_dep) == 0
    assert len(all_issues) == 1
