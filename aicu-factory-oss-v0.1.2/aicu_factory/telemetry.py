from __future__ import annotations

from typing import Any

import requests

from .config import Settings


SAFE_RESULT_KEYS = {
    "stress",
    "collapse_prob",
    "cascade_size_mean",
    "cascade_size_std",
    "topology",
    "model",
    "memory_alpha",
    "retry_limit",
    "runs",
    "timestamp",
}


def maybe_upload_result(settings: Settings, payload: dict[str, Any]) -> bool:
    if not settings.telemetry_enabled or not settings.telemetry_endpoint:
        return False
    safe_payload = {k: v for k, v in payload.items() if k in SAFE_RESULT_KEYS}
    if not safe_payload:
        return False
    response = requests.post(settings.telemetry_endpoint, json=safe_payload, timeout=20)
    response.raise_for_status()
    return True
