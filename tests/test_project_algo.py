import mock
import pytest
import tests.fakes as fakes

import ia.project.algo as algo
from ia.common.jira.sprint import Sprint
from ia.common.jira.issue import IssueCache


@pytest.fixture()
def jira_mock():
    m = mock.MagicMock()
    i1 = fakes.Issue("ISSUE-1")
    i2 = fakes.Issue("ISSUE-2")
    i3 = fakes.Issue("ISSUE-3")
    i4 = fakes.Issue("ISSUE-4")
    m.search_issues.return_value = [i1, i2, i3, i4]
    return m


def test_execution_progress_0(jira_mock):
    epic_key = "DANMR-609"
    percentage, all_issues, done_issues = algo.progress(jira_mock, epic_key)
    assert percentage == 0.0
    assert len(all_issues) == 4
    assert done_issues == []