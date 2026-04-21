from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


def utc_ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def make_report_content(job_name: str, line: str, kind: str, payload: dict[str, Any]) -> str:
    lines = [
        "# AICU Factory Report",
        "",
        f"- Job: {job_name}",
        f"- Line: {line}",
        f"- Kind: {kind}",
        f"- Generated at: {utc_ts()}",
        "",
        "## Payload",
        "```json",
        json.dumps(payload, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Status",
        "SUCCESS",
    ]
    return "\n".join(lines)


def make_figures_stub(job_name: str, line: str, payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "AICU FACTORY FIGURE STUB",
            f"Job: {job_name}",
            f"Line: {line}",
            f"Generated at: {utc_ts()}",
            f"Payload keys: {', '.join(sorted(payload.keys())) or '(none)'}",
        ]
    )
