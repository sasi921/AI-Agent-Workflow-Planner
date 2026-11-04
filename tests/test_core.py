import pytest
from planner.core import Step, WorkflowPlanner, PlanError

TOOLS = {'echo': lambda text: text}

def test_topological_order():
    p = WorkflowPlanner(TOOLS)
    steps = [Step('b', 'echo', {'text':'b'}, ('a',)), Step('a', 'echo', {'text':'a'})]
    assert [s.id for s in p.order(steps)] == ['a', 'b']

def test_approval_blocks_action():
    p = WorkflowPlanner(TOOLS)
    steps = [Step('a','echo',{'text':'a'},requires_approval=True), Step('b','echo',{'text':'b'},('a',))]
    result = p.run(steps, dry_run=False)
    assert [x['status'] for x in result['events']] == ['approval_required','blocked_by_dependency']
    assert p.run(steps, approved={'a'}, dry_run=False)['results'] == {'a':'a','b':'b'}

def test_cycle_rejected():
    with pytest.raises(PlanError, match='cycle'):
        WorkflowPlanner(TOOLS).order([Step('a','echo',{},('b',)), Step('b','echo',{},('a',))])

def test_missing_dependency_rejected():
    with pytest.raises(PlanError, match='Missing'):
        WorkflowPlanner(TOOLS).order([Step('a','echo',{},('missing',))])

def test_duplicate_id_rejected():
    with pytest.raises(PlanError, match='Duplicate'):
        WorkflowPlanner(TOOLS).order([Step('a','echo',{}), Step('a','echo',{})])

def test_unknown_tool_rejected():
    with pytest.raises(PlanError, match='Unknown'):
        WorkflowPlanner(TOOLS).order([Step('a','unknown',{})])

def test_dry_run_never_executes():
    calls=[]
    p=WorkflowPlanner({'x':lambda: calls.append('called')})
    assert p.run([Step('a','x',{})])['events'][0]['status']=='dry_run'
    assert calls==[]

def test_failure_blocks_dependents():
    def fail(): raise RuntimeError('oops')
    p=WorkflowPlanner({'fail':fail,'echo':lambda:True})
    out=p.run([Step('a','fail',{}),Step('b','echo',{},('a',))],dry_run=False)
    assert [e['status'] for e in out['events']]==['failed','blocked_by_dependency']
