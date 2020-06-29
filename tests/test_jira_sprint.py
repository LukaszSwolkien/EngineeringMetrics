import datetime

import pytest
from mock import MagicMock, Mock, PropertyMock

from ia.common.jira.sprint import DATE_TIME_FORMAT, Sprint

# import tests.fakes as fakes


def test_sprint_parser():
    test_data = 'com.atlassian.greenhopper.service.sprint.Sprint@28c838e2[id=8455,rapidViewId=3498,state=CLOSED,name=Sprint 24,startDate=2020-04-22T13:58:48.202Z,endDate=2020-05-06T13:58:00.000Z,completeDate=2020-05-06T14:11:07.481Z,activatedDate=2020-04-22T13:58:48.202Z,sequence=8455,goal=Churn Journey, demo for Account Balance]'
    test_sprint = Sprint(test_data)
    #pylint: disable = E
    assert test_sprint.name == 'Sprint 24'
    assert test_sprint.id == 8455
    assert test_sprint.state == 'CLOSED'
    assert test_sprint.startDate == '2020-04-22T13:58:48.202Z'
    assert test_sprint.goal == 'Churn Journey, demo for Account Balance'

    start_date = datetime.datetime.strptime(test_sprint.startDate, DATE_TIME_FORMAT)
    assert start_date.day == 22
    assert start_date.month == 4
    assert start_date.year == 2020
    assert start_date.hour == 13
    assert start_date.minute == 58
    assert start_date.second == 48
