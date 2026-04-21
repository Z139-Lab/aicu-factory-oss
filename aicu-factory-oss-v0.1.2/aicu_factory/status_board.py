from __future__ import annotations

from collections import Counter
from typing import Iterable

from .db import JobRecord


def render_status_board(jobs: Iterable[JobRecord]) -> str:
    jobs = list(jobs)
    counts = Counter(job.status for job in jobs)
    total_cost = sum(float(job.cost or 0.0) for job in jobs)
    lines = [
        'AICU Factory Status Board',
        '=========================',
        f'Total jobs: {len(jobs)}',
        f'Queued: {counts.get("queued", 0)}',
        f'Running: {counts.get("running", 0)}',
        f'Done: {counts.get("done", 0)}',
        f'Failed: {counts.get("failed", 0)}',
        f'Paused: {counts.get("paused", 0)}',
        f'Cancelled: {counts.get("cancelled", 0)}',
        f'Accumulated cost: {total_cost:.4f}',
        '',
        'Recent jobs:',
    ]
    for job in jobs[-5:]:
        lines.append(f'- {job.status:10} {job.kind:10} {job.name} ({job.id[:8]})')
    if len(jobs) == 0:
        lines.append('- none')
    return '\n'.join(lines)
