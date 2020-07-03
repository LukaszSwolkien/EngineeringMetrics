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
    created_defects, resolved_defects = algo.maintenance_trend(
        jira_mock, "PRJ", "01-01-2020", "30-01-2020"
    )
