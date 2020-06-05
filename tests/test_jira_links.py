import pytest
from mock import Mock, PropertyMock, MagicMock
from jira import Issue
from ia.jira import links as issuelinks
import tests.fakes as fakes


@pytest.fixture
def issue_mock():
    m = MagicMock()
    type(m.fields.project).key = PropertyMock(return_value="COE")
    type(m.fields).issuelinks = PropertyMock(return_value=[
        fakes.IssueLink("inwardIssue", f"{m.fields.project.key}-1"),
        fakes.IssueLink("inwardIssue", f"{m.fields.project.key}-2"),
        fakes.IssueLink("inwardIssue", "EXT-1", "Blocks"),
        fakes.IssueLink("outwardIssue", "EXT-2"),
    ])
    return m


def test_get_dependencies_no_external(issue_mock):
    links = issuelinks.get_external_dependencies(issue_mock)
    assert ["EXT-1", "EXT-2"] == [i.key for i in links]

    mock_issuelinks = PropertyMock(return_value=[
        fakes.IssueLink("inwardIssue", f"{issue_mock.fields.project.key}-1"),
        fakes.IssueLink("inwardIssue", f"{issue_mock.fields.project.key}-2"),
    ])
    type(issue_mock.fields).issuelinks = mock_issuelinks
    links = issuelinks.get_external_dependencies(issue_mock)
    assert links == []


def test_get_dependencies_1_external(issue_mock):
    mock_issuelinks = PropertyMock(return_value=[
        fakes.IssueLink("inwardIssue", f"{issue_mock.fields.project.key}-1"),
        fakes.IssueLink("outwardIssue", f"EXT-111"),
    ])
    type(issue_mock.fields).issuelinks = mock_issuelinks
    links = issuelinks.get_external_dependencies(issue_mock)
    assert ["EXT-111"] == [i.key for i in links]

def test_is_internal(issue_mock):
    assert not issuelinks.is_internal("EXT-123", "EXT-INTERNAL")
    assert not issuelinks.is_internal("EXT-4632", "INTERNAL")
    assert not issuelinks.is_internal("EXT-1", "EXTERNAL")


def test_get_external_blocked_by(issue_mock):
    links = issuelinks.get_external_blocked_by(issue_mock)
    assert links == []

    mock_issuelinks = PropertyMock()
    mock_issuelinks.return_value = [
        fakes.IssueLink("outwardIssue", "EXT-2", "Blocks")
    ]
    type(issue_mock.fields).issuelinks = mock_issuelinks
    links = issuelinks.get_external_blocked_by(issue_mock)
    assert links == ["EXT-2"]
