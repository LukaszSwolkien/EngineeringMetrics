import datetime as dt

import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

import ia.dependency.metrics_store as metrics
import tests.fakes as fakes


@pytest.fixture(autouse=True)
def db_mock():
    print("setup test_metrics db")
    metrics.__db = TinyDB(storage=MemoryStorage)
    yield
    print("teardown")



@pytest.fixture()
def all_issues():
    i1 = fakes.Issue('ISSUE-1')
    i2 = fakes.Issue('ISSUE-2')
    i3 = fakes.Issue('ISSUE-3')
    i4 = fakes.Issue('ISSUE-4')
    return [i1, i2, i3, i4]



def test_save(all_issues):
    metrics.save("ut", "test_squad", 100, all_issues, [])
    
def test_select_in(all_issues):
    metrics.save("ut", "test_squad", 75, all_issues, [all_issues[0]])
    earlier_dt = dt.datetime.now() - dt.timedelta(days=1)
    later_dt = dt.datetime.now() + dt.timedelta(days=1)
    found = metrics.select_in(earlier_dt, later_dt)
    assert len(found) == 1

def test_read_independence_stats(all_issues):
    metrics.save("ut", "test_squad", 75, all_issues, [all_issues[0]])
    metrics_history = metrics.read_independence_stats('ut', "other squad")
    assert metrics_history == None
    metrics_history = metrics.read_independence_stats('wrong name', "test_squad")
    assert metrics_history == None
    metrics_history = metrics.read_independence_stats('ut', "test_squad")
    assert isinstance(metrics_history, metrics.IndependenceMetrics)

def test_merge(all_issues):
    metrics.save("ut", "test_squad_1", 50, all_issues, [all_issues[0], all_issues[1]])
    i1 = fakes.Issue('ISSUE-5')
    i2 = fakes.Issue('ISSUE-6')
    i3 = fakes.Issue('ISSUE-7')
    i4 = fakes.Issue('ISSUE-8')
    all_issues_2 = [i1, i2, i3, i4]

    metrics.save("ut", "test_squad_2", 100, all_issues_2, [])
    metrics_history_1 = metrics.read_independence_stats('ut', "test_squad_1")
    metrics_history_2 = metrics.read_independence_stats('ut', "test_squad_2")
    total_metrics = metrics.merge([metrics_history_1, metrics_history_2])

    m = total_metrics.latest

    assert m['squad'] == 'Merged'
    assert m['name'] == 'ut'
    assert m['independence'] == 75
    assert len(m['all_issues']) == 8
    assert len(m['all_with_dep']) == 2
