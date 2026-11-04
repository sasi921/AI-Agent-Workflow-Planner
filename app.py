"""Run a JSON workflow with safe local demo tools."""
import argparse
import json
from pathlib import Path
from planner.core import Step, WorkflowPlanner

def word_count(text: str) -> int:
    return len(text.split())

def uppercase(text: str) -> str:
    return text.upper()

def main():
    parser = argparse.ArgumentParser(description='Approval-gated DAG workflow agent')
    parser.add_argument('workflow', nargs='?', default='examples/workflow.json')
    parser.add_argument('--execute', action='store_true', help='Execute demo tools instead of dry run')
    parser.add_argument('--approve', action='append', default=[], metavar='STEP_ID')
    args = parser.parse_args()
    data = json.loads(Path(args.workflow).read_text(encoding='utf-8'))
    steps = [Step(id=s['id'], tool=s['tool'], args=s.get('args', {}),
                  depends_on=tuple(s.get('depends_on', [])),
                  requires_approval=s.get('requires_approval', False)) for s in data['steps']]
    planner = WorkflowPlanner({'word_count': word_count, 'uppercase': uppercase})
    print(json.dumps(planner.run(steps, set(args.approve), dry_run=not args.execute), indent=2))

if __name__ == '__main__':
    main()
