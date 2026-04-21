from __future__ import annotations

import json
from pathlib import Path
from typing import Any


Z_PRESET_LIBRARY: dict[str, dict[str, Any]] = {
    'baseline': {
        'run_meta': {'z_ref': 1.39, 'preset': 'baseline'},
        'parameters': {'runs': 10},
        'safety_boundaries': {'allow_softening': True, 'allow_fallback_L': True},
        'repair_policy': {'max_attempts': 1},
        'alarm_policy': {'z_ref_tolerance': 0.08, 'chi_upper_guard': 1e12, 'dead_data_variance_floor': 1e-9},
    },
    'safe_scan': {
        'run_meta': {'z_ref': 1.39, 'preset': 'safe_scan'},
        'parameters': {'runs': 6, 'stress_grid': [0.88, 0.90, 0.92]},
        'safety_boundaries': {'allow_softening': True, 'allow_fallback_L': True, 'forbidden_constant_change': True},
        'repair_policy': {'max_attempts': 1, 'allowed': ['logistic_softening', 'fallback_L'], 'forbidden': ['change_z_ref']},
        'alarm_policy': {'z_ref_tolerance': 0.08, 'chi_upper_guard': 1e11, 'dead_data_variance_floor': 1e-9},
    },
    'paper_mode': {
        'run_meta': {'z_ref': 1.39, 'preset': 'paper_mode'},
        'parameters': {'runs': 20},
        'safety_boundaries': {'allow_softening': True, 'allow_fallback_L': False, 'forbidden_constant_change': True},
        'repair_policy': {'max_attempts': 0, 'allowed': [], 'forbidden': ['change_z_ref', 'change_grid_midrun']},
        'alarm_policy': {'z_ref_tolerance': 0.05, 'chi_upper_guard': 1e10, 'dead_data_variance_floor': 1e-8},
    },
}


def list_preset_names() -> list[str]:
    return sorted(Z_PRESET_LIBRARY)


def merge_manifest_with_preset(base_payload: dict[str, Any], preset_name: str) -> dict[str, Any]:
    if preset_name not in Z_PRESET_LIBRARY:
        raise KeyError(f'Unknown preset: {preset_name}')
    preset = Z_PRESET_LIBRARY[preset_name]
    merged = json.loads(json.dumps(base_payload))
    for section, values in preset.items():
        current = merged.setdefault(section, {})
        if isinstance(current, dict):
            for key, value in values.items():
                current.setdefault(key, value)
        else:
            merged[section] = values
    merged.setdefault('run_meta', {})['preset'] = preset_name
    return merged


def load_preset_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    preset_name = payload.get('preset_name') or payload.get('preset')
    if not preset_name:
        raise ValueError(f'Preset file missing preset_name: {path}')
    if preset_name not in Z_PRESET_LIBRARY:
        raise KeyError(f'Unknown preset_name {preset_name} in {path}')
    return {'preset_name': preset_name, 'notes': payload.get('notes', '')}
