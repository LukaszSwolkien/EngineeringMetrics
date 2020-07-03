import mock
import pytest

import ia.execution.algo as algo
import tests.fakes as fakes
from ia.common.jira.issue import IssueCache
from ia.common.jira.sprint import Sprint


@pytest.fixture()
def jira_mock():
    m = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1")
    i2 = fakes.Issue("ISSUE-2")
    i3 = fakes.Issue("ISSUE-3")
    i4 = fakes.Issue("ISSUE-4")
    m.search_issues.return_value = [i1, i2, i3, i4]
    return m


@pytest.fixture()
def sprint_mock():
    test_data = "test[id=8455,rapidViewId=3498,state=CLOSED,name=Sprint 24,startDate=2020-04-22T13:58:48.202Z,endDate=2020-05-06T13:58:00.000Z,completeDate=2020-05-06T14:11:07.481Z,activatedDate=2020-04-22T13:58:48.202Z,sequence=8455,goal=Churn Journey, demo for Account Balance]"
    sprint = Sprint(test_data)
    return sprint


def test_execution_progress_0(jira_mock):
    percentage, all_issues, done_issues = algo.progress(jira_mock, "jql")
    assert percentage == 0.0
    assert len(all_issues) == 4
    assert done_issues == []


def test_execution_progress_100():
    jira_mock = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1", "Done")
    i2 = fakes.Issue("ISSUE-2", "Done")
    i3 = fakes.Issue("ISSUE-3", "Done")
    i4 = fakes.Issue("ISSUE-4", "Done")
    jira_mock.search_issues.return_value = [i1, i2, i3, i4]

    percentage, all_issues, done_issues = algo.progress(jira_mock, "jql")
    assert percentage == 100.0
    assert len(all_issues) == 4
    assert len(done_issues) == 4


def test_execution_metrics(sprint_mock):
    jira_mock = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1", "Done")
    i2 = fakes.Issue("ISSUE-2", "Done")
    i3 = fakes.Issue("ISSUE-3", "Done")
    i4 = fakes.Issue("ISSUE-4", "In progress")
    jira_mock.search_issues.return_value = [i1, i2, i3, i4]

    _, all_issues, done_in_sprint = algo.progress(jira_mock, "jql")

    i4.fields.status.name = "Done"
    done_by_now = done_in_sprint + [IssueCache(jira_mock, i4)]

    em = algo.ExecutionMetrics(all_issues, done_in_sprint, done_by_now, sprint_mock)
    assert em.count_done_by_now == 4
    assert em.count_done_in_sprint == 3
    assert em.progress_by_now == 100
    assert em.progress_in_sprint == 75


def test_active_sprint_progress():
    jira_mock = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1", "Done")
    i2 = fakes.Issue("ISSUE-2", "Done")
    i3 = fakes.Issue("ISSUE-3", "In progress")
    i4 = fakes.Issue("ISSUE-4", "Open")
    jira_mock.search_issues.return_value = [i1, i2, i3, i4]

    percentage, all_issues, done_issues = algo.active_sprint_progress(jira_mock, "PRJ_KEY")
    assert percentage == 50.0
    assert len(all_issues) == 4
    assert done_issues[0].key == IssueCache(jira_mock, i1).key
    assert done_issues[1].key == IssueCache(jira_mock, i2).key


def test_all_sprints(sprint_mock):
    jira_mock = mock.MagicMock()
    jira_mock.sprints.return_value = [sprint_mock]
    found_sprints = algo.all_sprints(jira_mock, 1)
    assert found_sprints == [sprint_mock]


def test_blocked_during_sprint(jira_mock, sprint_mock):
    blocked = algo.blocked_during_sprint(jira_mock, "UT", sprint_mock)
    assert blocked == []


def test_last_sprints(jira_mock, sprint_mock):
    jira_mock.boards.return_value = mock.MagicMock()
    jira_mock.sprints.return_value = [sprint_mock]

    sprints = algo.last_sprints(jira_mock, "board name")
    assert len(sprints) == 2  # one active and one closed


def test_progress_history(jira_mock, sprint_mock):
    jira_mock.sprints.return_value = [sprint_mock]
    found_sprints = algo.all_sprints(jira_mock, 1)
    history = algo.progress_history(jira_mock, "PRJ", found_sprints)
    assert len(history) == 1


def test_sprint_churn(jira_mock, sprint_mock):
    issues_added, issues_removed, issues_blocked, issues_unblocked = algo.sprint_churn(
        jira_mock, "PRJ", sprint_mock
    )
    assert len(issues_added) == 0
    assert len(issues_removed) == 0
    assert len(issues_blocked) == 0
    assert len(issues_unblocked) == 0


def test_sprint_churn_history(jira_mock, sprint_mock):
    history = algo.progress_history(jira_mock, "PRJ", [sprint_mock])
    labels, added, removed, unblocked, blocked = algo.sprint_churn_history(
        jira_mock, "PRJ", history
    )

    assert labels[0] == sprint_mock.name
    assert added[0] == 0
    assert removed[0] == 0
    assert blocked[0] == 0
    assert unblocked[0] == 0
