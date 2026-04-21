from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any

from .artifacts import utc_ts, write_json, write_text
from .presets import list_preset_names, merge_manifest_with_preset


@dataclass(slots=True)
class ZManifest:
    payload: dict[str, Any]

    @property
    def run_meta(self) -> dict[str, Any]:
        return self.payload.get('run_meta', {})

    @property
    def parameters(self) -> dict[str, Any]:
        return self.payload.get('parameters', {})

    @property
    def safety_boundaries(self) -> dict[str, Any]:
        return self.payload.get('safety_boundaries', {})

    @property
    def repair_policy(self) -> dict[str, Any]:
        return self.payload.get('repair_policy', {})

    @property
    def alarm_policy(self) -> dict[str, Any]:
        return self.payload.get('alarm_policy', {})

    @property
    def experiment_id(self) -> str:
        return str(self.run_meta.get('experiment_id', 'z_experiment'))


def load_manifest(path: Path, preset_name: str | None = None) -> ZManifest:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if preset_name:
        payload = merge_manifest_with_preset(payload, preset_name)
    return ZManifest(payload)


def validate_manifest(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ['run_meta', 'parameters', 'safety_boundaries', 'repair_policy', 'alarm_policy']:
        if key not in payload or not isinstance(payload[key], dict):
            errors.append(f'Missing object: {key}')
    parameters = payload.get('parameters', {})
    if 'runs' in parameters and int(parameters['runs']) <= 0:
        errors.append('parameters.runs must be > 0')
    if 'stress_grid' in parameters and not isinstance(parameters['stress_grid'], list):
        errors.append('parameters.stress_grid must be a list')
    if 'L_grid' in parameters and not isinstance(parameters['L_grid'], list):
        errors.append('parameters.L_grid must be a list')
    return errors


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()[:8]


def materialize_run_plan(manifest: ZManifest) -> list[dict[str, Any]]:
    params = manifest.parameters
    stress_grid = params.get('stress_grid') or [params.get('stress', 0.9)]
    L_grid = params.get('L_grid') or [params.get('L', 1)]
    runs = int(params.get('runs', 1))
    matrix: list[dict[str, Any]] = []
    for stress, L in product(stress_grid, L_grid):
        matrix.append({'stress': stress, 'L': L, 'runs': runs})
    return matrix


def scaffold_project(root: Path, project_name: str) -> dict[str, str]:
    project_root = root / 'projects' / project_name
    manifests = project_root / 'manifests'
    presets = project_root / 'presets'
    runs = project_root / 'runs'
    docs = project_root / 'docs'
    for p in [manifests, presets, runs, docs]:
        p.mkdir(parents=True, exist_ok=True)
    sample_manifest = {
        'run_meta': {'experiment_id': f'{project_name}_baseline', 'z_ref': 1.39, 'run_family': project_name},
        'parameters': {'L_grid': [32000, 64000], 'stress_grid': [0.88, 0.90, 0.92], 'runs': 10},
        'safety_boundaries': {'allow_softening': True, 'allow_fallback_L': True, 'forbidden_constant_change': True},
        'repair_policy': {'max_attempts': 1, 'allowed': ['logistic_softening', 'fallback_L'], 'forbidden': ['change_z_ref']},
        'alarm_policy': {'z_ref_tolerance': 0.08, 'chi_upper_guard': 1e12, 'dead_data_variance_floor': 1e-9},
    }
    write_json(manifests / 'baseline.json', sample_manifest)
    for preset_name in list_preset_names():
        write_json(presets / f'{preset_name}.json', {'preset_name': preset_name, 'notes': f'Built-in preset: {preset_name}'})
    write_text(docs / 'README.md', f'# {project_name}\n\nProject scaffold for Z-Orchestrator style runs.\n')
    return {'project_root': str(project_root), 'manifest': str(manifests / 'baseline.json')}


def execute_manifest(manifest: ZManifest, workspace: Path) -> Path:
    run_hash = _stable_hash({'ts': utc_ts(), 'manifest': manifest.payload})
    run_dir = workspace / 'z_runs' / f'run_{run_hash}'
    run_dir.mkdir(parents=True, exist_ok=True)
    matrix = materialize_run_plan(manifest)
    summary = {
        'run_id': run_dir.name,
        'experiment_id': manifest.experiment_id,
        'run_family': manifest.run_meta.get('run_family', 'default'),
        'preset': manifest.run_meta.get('preset', 'custom'),
        'generated_at': utc_ts(),
        'matrix_points': len(matrix),
        'parameters': manifest.parameters,
        'safety_boundaries': manifest.safety_boundaries,
        'repair_policy': manifest.repair_policy,
        'alarm_policy': manifest.alarm_policy,
    }
    write_json(run_dir / 'manifest_snapshot.json', manifest.payload)
    write_json(run_dir / 'run_plan.json', {'matrix': matrix})
    write_json(run_dir / 'summary.json', summary)
    report = [
        f'# Z-Orchestrator Run Report: {manifest.experiment_id}',
        '',
        f"- Run family: {manifest.run_meta.get('run_family', 'default')}",
        f"- Preset: {summary['preset']}",
        f"- Generated at: {summary['generated_at']}",
        f"- Matrix points: {len(matrix)}",
        '',
        '## Safety Boundaries',
        '```json',
        json.dumps(manifest.safety_boundaries, indent=2, ensure_ascii=False),
        '```',
        '',
        '## Repair Policy',
        '```json',
        json.dumps(manifest.repair_policy, indent=2, ensure_ascii=False),
        '```',
        '',
        '## Alarm Policy',
        '```json',
        json.dumps(manifest.alarm_policy, indent=2, ensure_ascii=False),
        '```',
        '',
        '## Notes',
        'This OSS run scaffolds a clean run layout, preset-aware manifest, and plan. Attach your real simulator or pipeline in the next iteration.',
    ]
    write_text(run_dir / 'report.md', '\n'.join(report))
    return run_dir
