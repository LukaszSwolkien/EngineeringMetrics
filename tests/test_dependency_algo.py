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

def test_get_link_key():
    link_key = '101'
    link = fakes.IssueLink('inwardIssue', link_key)
    lk = dep.get_link_key(link)
    assert link_key == lk

def test_count_stats():
    issue_cache_1 = fakes.IssueCache(fakes.Issue('ISSUE-1', epic_name='my epic'))
    issue_cache_1.linked_issues = {"ISSUE-10": fakes.Issue('ISSUE-10', epic_name='linked epic')}
    issue_cache_2 = mock.MagicMock()
    issue_cache_2.linked_issues = {"ISSUE-20": fakes.Issue('ISSUE-20')}

    project_count, epic_count, link_epic_count = dep.count_stats([issue_cache_1, issue_cache_2])
    assert len(project_count) == 1
    assert len(epic_count) == 2 # 'my epic' and none
    assert len(link_epic_count) == 2 # none and linked epic


def test_count_internal():
    issue_cache_1 = fakes.IssueCache(fakes.Issue('ISSUE-1', epic_name='my epic'))
    issue_cache_1.linked_issues = {"ISSUE-10": fakes.Issue('ISSUE-10', epic_name='linked epic')}
    issue_cache_2 = mock.MagicMock()
    issue_cache_2.linked_issues = {"ISSUE-20": fakes.Issue('ISSUE-20')}
    counter = dep.count_internal([issue_cache_1, issue_cache_2], ['prj1', 'prj2'])
    assert len(counter['internal']) == 0
    assert len(counter['external']) == 2


def test_count_by_link_type():
    i1 = fakes.Issue('ISSUE-1', epic_name='my epic')
    i1.fields.issuelinks = [fakes.IssueLink('outwardIssue', 'DEP-1'), fakes.IssueLink('inwardIssue','DEP-2')]
    issue_cache_1 = fakes.IssueCache(i1)
    issue_cache_1.linked_issues = {"ISSUE-10": fakes.Issue('ISSUE-10', epic_name='linked epic')}
    issue_cache_2 = mock.MagicMock()
    issue_cache_2.linked_issues = {"ISSUE-20": fakes.Issue('ISSUE-20')}

    linked_issues = dep.count_by_link_type([issue_cache_1, issue_cache_2])
    assert linked_issues == {'Dependancy': 2}

# TODO - test cycle dependency: 
# DANCOE-1155
# DANCOE-1168
# DANCOE-1048

# DANCOE-1155
# DANCOE-1168
# DANCOE-1048

# DANCOE-1155
# DANCOE-1168
# DANCOE-1048

