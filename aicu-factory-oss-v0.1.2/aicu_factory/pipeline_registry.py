from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .artifacts import make_figures_stub, make_report_content, utc_ts, write_json, write_text


RunnerFunc = Callable[[Any, Any], Path]
EstimatorFunc = Callable[[dict[str, Any]], float]


@dataclass(frozen=True, slots=True)
class PipelineSpec:
    kind: str
    description: str
    default_line: str
    runner_name: str
    estimate_cost: EstimatorFunc


def _estimate_sweep(payload: dict[str, Any]) -> float:
    runs = int(payload.get('runs', 20) or 20)
    stress_grid = payload.get('stress_grid')
    stress_points = len(stress_grid) if isinstance(stress_grid, list) and stress_grid else 1
    return round(0.002 * runs * stress_points, 4)


def _estimate_topology(payload: dict[str, Any]) -> float:
    agents = int(payload.get('agents', 8) or 8)
    return round(0.01 + 0.001 * agents, 4)


def _estimate_report(_: dict[str, Any]) -> float:
    return 0.01


def _estimate_figures(_: dict[str, Any]) -> float:
    return 0.008


def _estimate_script(payload: dict[str, Any]) -> float:
    args = payload.get('args', [])
    return round(0.01 + 0.002 * len(args), 4)


def list_pipeline_specs() -> list[PipelineSpec]:
    return [
        PipelineSpec('sweep', 'Controlled research sweep across stress or parameter grids.', 'research', 'run_sweep', _estimate_sweep),
        PipelineSpec('topology', 'Topology analysis for chain, DAG, or related structures.', 'research', 'run_topology', _estimate_topology),
        PipelineSpec('report', 'Paper or client report artifact generation.', 'paper', 'run_report', _estimate_report),
        PipelineSpec('figures', 'Paper figure or summary artifact generation.', 'paper', 'run_figures', _estimate_figures),
        PipelineSpec('script', 'External script execution inside the workspace.', 'research', 'run_script', _estimate_script),
    ]


def get_pipeline_spec(kind: str) -> PipelineSpec | None:
    for spec in list_pipeline_specs():
        if spec.kind == kind:
            return spec
    return None


def run_report(job: Any, settings: Any) -> Path:
    artifact_path = settings.reports_dir / f'report_{job.id}.md'
    write_text(artifact_path, make_report_content(job.name, job.line, job.kind, job.payload))
    return artifact_path


def run_figures(job: Any, settings: Any) -> Path:
    artifact_path = settings.figures_dir / f'figures_{job.id}.txt'
    write_text(artifact_path, make_figures_stub(job.name, job.line, job.payload))
    return artifact_path


def run_sweep(job: Any, settings: Any) -> Path:
    payload = job.payload
    artifact_path = settings.runs_dir / f'run_{job.id}.json'
    write_json(artifact_path, {
        'job_id': job.id,
        'name': job.name,
        'line': job.line,
        'kind': job.kind,
        'payload': payload,
        'status': 'simulated_success',
        'estimated_cost': _estimate_sweep(payload),
        'finished_at': utc_ts(),
    })
    return artifact_path


def run_topology(job: Any, settings: Any) -> Path:
    payload = job.payload
    artifact_path = settings.runs_dir / f'run_{job.id}.json'
    write_json(artifact_path, {
        'job_id': job.id,
        'name': job.name,
        'line': job.line,
        'kind': job.kind,
        'payload': payload,
        'status': 'simulated_success',
        'estimated_cost': _estimate_topology(payload),
        'finished_at': utc_ts(),
    })
    return artifact_path
