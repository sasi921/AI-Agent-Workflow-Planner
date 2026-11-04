"""Deterministic DAG workflow planner with approval-gated actions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class Step:
    id: str
    tool: str
    args: dict[str, Any]
    depends_on: tuple[str, ...] = ()
    requires_approval: bool = False

class PlanError(ValueError):
    pass

class WorkflowPlanner:
    def __init__(self, tools: dict[str, Callable[..., Any]]):
        self.tools = tools

    def order(self, steps: list[Step]) -> list[Step]:
        ids = [s.id for s in steps]
        if len(ids) != len(set(ids)):
            raise PlanError('Duplicate step ID')
        by_id = {s.id: s for s in steps}
        for step in steps:
            if step.tool not in self.tools:
                raise PlanError(f'Unknown tool: {step.tool}')
            for dep in step.depends_on:
                if dep not in by_id:
                    raise PlanError(f'Missing dependency: {dep}')
        ordered, visited, visiting = [], set(), set()
        def visit(sid: str):
            if sid in visiting:
                raise PlanError('Dependency cycle detected')
            if sid in visited:
                return
            visiting.add(sid)
            for dep in by_id[sid].depends_on:
                visit(dep)
            visiting.remove(sid)
            visited.add(sid)
            ordered.append(by_id[sid])
        for step in steps:
            visit(step.id)
        return ordered

    def run(self, steps: list[Step], approved: set[str] | None = None, dry_run: bool = True) -> dict:
        ordered = self.order(steps)
        approved = approved or set()
        result: dict[str, Any] = {}
        events = []
        for step in ordered:
            if step.requires_approval and step.id not in approved:
                events.append({'step': step.id, 'status': 'approval_required'})
                continue
            if any(dep not in result for dep in step.depends_on):
                events.append({'step': step.id, 'status': 'blocked_by_dependency'})
                continue
            if dry_run:
                events.append({'step': step.id, 'status': 'dry_run', 'tool': step.tool})
                result[step.id] = None
                continue
            try:
                result[step.id] = self.tools[step.tool](**step.args)
                events.append({'step': step.id, 'status': 'completed'})
            except Exception as exc:
                events.append({'step': step.id, 'status': 'failed', 'error': str(exc)})
        return {'events': events, 'results': result}
