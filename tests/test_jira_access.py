import ia.exception as iae
from ia.jira import connect
import pytest
import os


def test_jira_access_wrong_credentials():
    with pytest.raises(iae.IAException):
        connect(os.environ['JIRA_URL'], ('fake_user', 'fake_password'), timeout=1.0)


def test_jira_access_wrong_url():
    with pytest.raises(iae.IAException):
        connect("https://jira.fake.com/",  (os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD']), timeout=1.0)


def test_jira_access():
    connect(os.environ['JIRA_URL'], (os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD']))