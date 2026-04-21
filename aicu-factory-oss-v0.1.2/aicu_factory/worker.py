from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .artifacts import utc_ts, write_json
from .config import Settings
from .cost_guard import check_job_cost
from .db import JobRecord, get_job, get_jobs_by_status, update_job
from .notifier import TelegramNotifier
from .pipeline_registry import get_pipeline_spec, run_figures, run_report, run_sweep, run_topology


class WorkerError(RuntimeError):
    pass


RUNNERS = {
    'report': run_report,
    'figures': run_figures,
    'sweep': run_sweep,
    'topology': run_topology,
}


def _run_script_job(job: JobRecord, settings: Settings) -> Path:
    payload = job.payload
    script_path = payload.get('script_path')
    if not script_path:
        raise WorkerError('Missing payload.script_path for script job')
    args = payload.get('args', [])
    output_name = payload.get('output_name', f'script_{job.id}.json')
    out_path = settings.runs_dir / output_name
    command = [sys.executable, script_path, *args]
    result = subprocess.run(command, cwd=settings.workspace, capture_output=True, text=True, check=False)
    run_payload = {
        'job_id': job.id,
        'command': command,
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'finished_at': utc_ts(),
    }
    write_json(out_path, run_payload)
    if result.returncode != 0:
        raise WorkerError(f'Script job failed with return code {result.returncode}')
    return out_path


def _resolve_runner(job: JobRecord):
    if job.kind == 'script':
        return _run_script_job
    runner = RUNNERS.get(job.kind)
    if runner is not None:
        return runner
    spec = get_pipeline_spec(job.kind)
    if spec is None:
        raise WorkerError(f'Unsupported job kind: {job.kind}')
    raise WorkerError(f'Runner not implemented for pipeline: {spec.kind}')


def run_single_job(job: JobRecord, settings: Settings, notifier: TelegramNotifier) -> Path:
    update_job(settings.db_path, job.id, status='running')
    artifact_path: Path | None = None
    try:
        runner = _resolve_runner(job)
        artifact_path = runner(job, settings)
        actual_cost = float(job.payload.get('cost_hint', 0.0)) or float(job.payload.get('estimated_cost', 0.0))
        if actual_cost <= 0:
            spec = get_pipeline_spec(job.kind)
            actual_cost = float(spec.estimate_cost(job.payload)) if spec is not None else 0.0
        update_job(
            settings.db_path,
            job.id,
            status='done',
            cost=actual_cost,
            artifact_path=str(artifact_path),
        )
        notifier.send(
            '\n'.join(
                [
                    '✅ AICU job completed',
                    f'Job: {job.name}',
                    f'Kind: {job.kind}',
                    f'Cost: {actual_cost:.4f}',
                    f'Artifact: {artifact_path}',
                ]
            )
        )
        return artifact_path
    except Exception as exc:
        update_job(settings.db_path, job.id, status='failed', error_message=str(exc))
        notifier.send(
            '\n'.join(
                [
                    '❌ AICU job failed',
                    f'Job: {job.name}',
                    f'Kind: {job.kind}',
                    f'Error: {exc}',
                ]
            )
        )
        raise


def run_batch(settings: Settings) -> list[Path]:
    notifier = TelegramNotifier.from_settings(settings)
    queued = get_jobs_by_status(settings.db_path, 'queued', limit=settings.max_run_per_batch)
    artifacts: list[Path] = []
    remaining_budget = float(settings.batch_budget)
    consecutive_failures = 0
    for job in queued:
        decision = check_job_cost(job, settings.max_job_cost, remaining_budget)
        if not decision.allowed:
            update_job(settings.db_path, job.id, status='paused', error_message=f'Cost guard: {decision.reason}')
            notifier.send('\n'.join(['⏸️ AICU job paused by cost guard', f'Job: {job.name}', f'Reason: {decision.reason}']))
            continue
        try:
            artifacts.append(run_single_job(job, settings, notifier))
            remaining_budget -= decision.estimated_cost
            latest = get_job(settings.db_path, job.id)
            if latest and latest.status == 'failed':
                consecutive_failures += 1
            else:
                consecutive_failures = 0
        except Exception:
            consecutive_failures += 1
        if consecutive_failures >= 2:
            break
    return artifacts
