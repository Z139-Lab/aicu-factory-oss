from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

VALID_STATUSES = {
    "queued",
    "running",
    "done",
    "paused",
    "failed",
    "cancelled",
}


def utc_ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


@dataclass(slots=True)
class JobRecord:
    id: str
    name: str
    line: str
    kind: str
    status: str
    cost: float
    payload_json: str
    artifact_path: str | None
    error_message: str | None
    created_at: str
    started_at: str | None
    finished_at: str | None
    updated_at: str

    @property
    def payload(self) -> dict[str, Any]:
        if not self.payload_json:
            return {}
        return json.loads(self.payload_json)


def get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                line TEXT NOT NULL,
                kind TEXT NOT NULL,
                status TEXT NOT NULL,
                cost REAL DEFAULT 0,
                payload_json TEXT DEFAULT '{}',
                artifact_path TEXT,
                error_message TEXT,
                created_at TEXT,
                started_at TEXT,
                finished_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.commit()


def add_job(
    db_path: Path,
    *,
    name: str,
    line: str,
    kind: str,
    status: str = "queued",
    cost: float = 0.0,
    payload: dict[str, Any] | None = None,
) -> str:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    now = utc_ts()
    job_id = str(uuid.uuid4())
    payload_json = json.dumps(payload or {}, ensure_ascii=False)
    with get_conn(db_path) as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, name, line, kind, status, cost, payload_json,
                artifact_path, error_message, created_at, started_at, finished_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                name,
                line,
                kind,
                status,
                cost,
                payload_json,
                None,
                None,
                now,
                None,
                None,
                now,
            ),
        )
        conn.commit()
    return job_id


def _row_to_record(row: sqlite3.Row) -> JobRecord:
    return JobRecord(**dict(row))


def list_jobs(db_path: Path) -> list[JobRecord]:
    with get_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY created_at ASC"
        ).fetchall()
    return [_row_to_record(row) for row in rows]


def get_job(db_path: Path, job_id: str) -> JobRecord | None:
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_record(row) if row else None


def get_jobs_by_status(db_path: Path, status: str, limit: int | None = None) -> list[JobRecord]:
    query = "SELECT * FROM jobs WHERE status = ? ORDER BY created_at ASC"
    params: list[Any] = [status]
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    with get_conn(db_path) as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
    return [_row_to_record(row) for row in rows]


def update_job(
    db_path: Path,
    job_id: str,
    *,
    status: str | None = None,
    error_message: str | None = None,
    cost: float | None = None,
    artifact_path: str | None = None,
) -> None:
    now = utc_ts()
    current = get_job(db_path, job_id)
    if not current:
        raise ValueError(f"Job not found: {job_id}")
    new_status = status or current.status
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")
    started_at = current.started_at
    finished_at = current.finished_at
    if status == "running" and not started_at:
        started_at = now
    if status in {"done", "failed", "cancelled"}:
        finished_at = now
    with get_conn(db_path) as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, error_message = ?, cost = ?, artifact_path = ?,
                started_at = ?, finished_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                new_status,
                error_message,
                current.cost if cost is None else cost,
                current.artifact_path if artifact_path is None else artifact_path,
                started_at,
                finished_at,
                now,
                job_id,
            ),
        )
        conn.commit()
