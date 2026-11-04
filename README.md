# AI Agent Workflow Planner

A dependency-aware, approval-gated workflow agent built with Python's standard library. A practical standalone AI-agent engineering lab project focused on the **planning and execution layer** of agentic systems (not an LLM-backed planner).

## Features

- Deterministic topological planning for multi-step DAG workflows
- Cycle, missing-dependency, duplicate-step, and unknown-tool validation
- Human approval required before flagged actions run
- Dry-run mode enabled by default
- Explicit tool allowlist and dependency-aware failure handling
- JSON workflow inputs, CLI, pytest suite, and GitHub Actions CI

## Quick start

```bash
python app.py
python app.py --execute
python app.py --execute --approve publish
python -m pip install -r requirements.txt
python -m pytest -q
```

The example includes an `inspect` step and a `publish` step that requires explicit approval. The `publish` demo tool only uppercases a string; **it does not publish externally**. Integrate real tools only after adding authentication, permission checks, idempotency, and audit logging.

## How it works

1. Parse workflow steps from JSON.
2. Validate tool names, dependencies, and unique IDs.
3. Topologically sort the DAG; reject cycles.
4. Execute in dependency order, or dry-run without side effects.
5. Block actions without approval or whose dependencies failed.
6. Return structured events and results.

## Next steps

Add a constrained LLM planner with schema validation, state persistence, resumable approvals, retry policies, observability, and real integrations with least-privilege credentials.

## License

MIT
