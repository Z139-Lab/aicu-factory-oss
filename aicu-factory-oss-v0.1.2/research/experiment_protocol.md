# Experiment Protocol Draft

## Goal
Run controlled, reproducible AI experiments with explicit manifests, bounded budgets, and exportable results.

## Minimal protocol
1. Initialize the workspace.
2. Select a pipeline type.
3. Choose a preset or provide a manifest.
4. Validate manifest safety boundaries.
5. Execute through the worker.
6. Inspect artifacts and summary outputs.
7. Export validated datasets.

## Recommended conventions
- Keep prompts, secrets, and user content out of shared datasets.
- Export only structured aggregate metrics for sharing.
- Track model name, topology, retries, memory/control parameters, and run timestamps.
- Use paper_mode for publication-facing runs and baseline/safe_scan for development.

## Artifact expectations
- summary.json
- report.md
- figures/ (when applicable)
- manifest_snapshot.json
- run_plan.json
