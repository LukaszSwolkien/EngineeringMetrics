import os

import pytest

import ia.common.exception as iae
from ia.common.jira.connection import connect


def test_jira_access_wrong_credentials():
    with pytest.raises(iae.IAException):
        connect(os.environ['JIRA_URL'], ('fake_user', 'fake_password'), timeout=0.1, max_retries=0)


def test_jira_access_wrong_url():
    with pytest.raises(iae.IAException):
        connect("https://jira.fake.com/",  (os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD']), timeout=0.1, max_retries=0)


def test_jira_access():
    connect(os.environ['JIRA_URL'], (os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD']), timeout=3, max_retries=3)
