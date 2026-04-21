from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(dotenv_path: str = '.env') -> None:
    path = Path(dotenv_path)
    if not path.exists():
        return
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


@dataclass(slots=True)
class Settings:
    db_path: Path
    workspace: Path
    max_run_per_batch: int
    batch_budget: float
    max_job_cost: float
    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str
    telemetry_enabled: bool
    telemetry_endpoint: str
    z_projects_dirname: str

    @property
    def reports_dir(self) -> Path:
        return self.workspace / 'reports'

    @property
    def figures_dir(self) -> Path:
        return self.workspace / 'figures'

    @property
    def logs_dir(self) -> Path:
        return self.workspace / 'logs'

    @property
    def runs_dir(self) -> Path:
        return self.workspace / 'runs'

    @property
    def data_dir(self) -> Path:
        return self.workspace / 'data'

    @property
    def z_runs_dir(self) -> Path:
        return self.workspace / 'z_runs'

    @property
    def z_projects_dir(self) -> Path:
        return self.workspace / self.z_projects_dirname


def load_settings() -> Settings:
    workspace = Path(os.getenv('AICU_WORKSPACE', 'workspace'))
    db_path = Path(os.getenv('AICU_DB_PATH', str(workspace / 'jobs.db')))
    return Settings(
        db_path=db_path,
        workspace=workspace,
        max_run_per_batch=int(os.getenv('AICU_MAX_RUN_PER_BATCH', '3')),
        batch_budget=float(os.getenv('AICU_BATCH_BUDGET', '1.0')),
        max_job_cost=float(os.getenv('AICU_MAX_JOB_COST', '0.5')),
        telegram_enabled=_as_bool(os.getenv('AICU_TELEGRAM_ENABLED'), False),
        telegram_bot_token=os.getenv('AICU_TELEGRAM_BOT_TOKEN', ''),
        telegram_chat_id=os.getenv('AICU_TELEGRAM_CHAT_ID', ''),
        telemetry_enabled=_as_bool(os.getenv('AICU_TELEMETRY_ENABLED'), False),
        telemetry_endpoint=os.getenv('AICU_TELEMETRY_ENDPOINT', ''),
        z_projects_dirname=os.getenv('AICU_Z_PROJECTS_DIR', 'projects'),
    )


def ensure_workspace(settings: Settings) -> None:
    settings.workspace.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.figures_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.z_runs_dir.mkdir(parents=True, exist_ok=True)
    settings.z_projects_dir.mkdir(parents=True, exist_ok=True)
