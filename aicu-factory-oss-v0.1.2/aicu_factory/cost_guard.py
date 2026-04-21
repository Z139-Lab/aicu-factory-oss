from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .pipeline_registry import get_pipeline_spec


@dataclass(frozen=True, slots=True)
class CostDecision:
    allowed: bool
    estimated_cost: float
    reason: str


def estimate_job_cost(job: Any) -> float:
    payload = job.payload
    if isinstance(payload.get('cost_hint'), (int, float)):
        return float(payload['cost_hint'])
    spec = get_pipeline_spec(job.kind)
    if spec is None:
        return 0.0
    return float(spec.estimate_cost(payload))


def check_job_cost(job: Any, max_job_cost: float, remaining_batch_budget: float) -> CostDecision:
    estimated = estimate_job_cost(job)
    if estimated > max_job_cost:
        return CostDecision(False, estimated, f'estimated cost {estimated:.4f} exceeds max job cost {max_job_cost:.4f}')
    if estimated > remaining_batch_budget:
        return CostDecision(False, estimated, f'estimated cost {estimated:.4f} exceeds remaining batch budget {remaining_batch_budget:.4f}')
    return CostDecision(True, estimated, 'allowed')
