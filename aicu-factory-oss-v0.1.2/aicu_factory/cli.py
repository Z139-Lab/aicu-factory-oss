from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import ensure_workspace, load_settings
from .db import add_job, get_job, init_db, list_jobs, update_job
from .notifier import TelegramNotifier
from .pipeline_registry import list_pipeline_specs
from .presets import list_preset_names
from .status_board import render_status_board
from .worker import run_batch
from .z_orchestrator import execute_manifest, load_manifest, scaffold_project, validate_manifest


def cmd_init(_: argparse.Namespace) -> int:
    settings = load_settings()
    ensure_workspace(settings)
    init_db(settings.db_path)
    print(f'[OK] Workspace ready: {settings.workspace}')
    print(f'[OK] DB ready: {settings.db_path}')
    print(f'[OK] Z projects dir: {settings.z_projects_dir}')
    print(f'[OK] Batch budget: {settings.batch_budget:.4f}')
    print(f'[OK] Max job cost: {settings.max_job_cost:.4f}')
    return 0


def cmd_add_demo(_: argparse.Namespace) -> int:
    settings = load_settings()
    ensure_workspace(settings)
    init_db(settings.db_path)
    demo_ids = [
        add_job(settings.db_path, name='Research sweep demo', line='research', kind='sweep', payload={'stress': 0.92, 'runs': 20}),
        add_job(settings.db_path, name='Topology analysis demo', line='research', kind='topology', payload={'topology': 'dag', 'agents': 8}),
        add_job(settings.db_path, name='Paper report demo', line='paper', kind='report', payload={'title': 'Demo criticality report'}),
        add_job(settings.db_path, name='Paper figures demo', line='paper', kind='figures', payload={'figure_set': 'main'}),
    ]
    print('[OK] Demo jobs queued')
    for job_id in demo_ids:
        print(job_id)
    return 0


def cmd_add_script(args: argparse.Namespace) -> int:
    settings = load_settings()
    ensure_workspace(settings)
    init_db(settings.db_path)
    job_id = add_job(
        settings.db_path,
        name=args.name,
        line=args.line,
        kind='script',
        payload={
            'script_path': args.script,
            'args': args.script_args,
            'output_name': args.output_name,
            'cost_hint': args.cost_hint,
        },
    )
    print(f'[OK] Script job queued: {job_id}')
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    settings = load_settings()
    init_db(settings.db_path)
    jobs = list_jobs(settings.db_path)
    if not jobs:
        print('No jobs found')
        return 0
    print(f"{'ID':36} {'STATUS':10} {'LINE':10} {'KIND':12} {'COST':8} NAME")
    print('-' * 118)
    for job in jobs:
        print(f"{job.id:36} {job.status:10} {job.line:10} {job.kind:12} {job.cost:8.4f} {job.name}")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    settings = load_settings()
    init_db(settings.db_path)
    print(render_status_board(list_jobs(settings.db_path)))
    return 0


def cmd_list_pipelines(_: argparse.Namespace) -> int:
    for spec in list_pipeline_specs():
        print(f'{spec.kind:12} line={spec.default_line:8} runner={spec.runner_name:14} {spec.description}')
    return 0


def cmd_list_presets(_: argparse.Namespace) -> int:
    for name in list_preset_names():
        print(name)
    return 0


def _status_transition(job_id: str, status: str) -> int:
    settings = load_settings()
    init_db(settings.db_path)
    if not get_job(settings.db_path, job_id):
        print('[ERR] Job not found')
        return 1
    update_job(settings.db_path, job_id, status=status, error_message=None)
    print(f'[OK] Job -> {status}: {job_id}')
    return 0


def cmd_pause(args: argparse.Namespace) -> int:
    return _status_transition(args.job_id, 'paused')


def cmd_resume(args: argparse.Namespace) -> int:
    return _status_transition(args.job_id, 'queued')


def cmd_cancel(args: argparse.Namespace) -> int:
    return _status_transition(args.job_id, 'cancelled')


def cmd_retry(args: argparse.Namespace) -> int:
    return _status_transition(args.job_id, 'queued')


def cmd_run(_: argparse.Namespace) -> int:
    settings = load_settings()
    ensure_workspace(settings)
    init_db(settings.db_path)
    artifacts = run_batch(settings)
    if not artifacts:
        print('No queued jobs processed')
        return 0
    print('[OK] Processed artifacts:')
    for path in artifacts:
        print(path)
    print('')
    print(render_status_board(list_jobs(settings.db_path)))
    return 0


def cmd_test_telegram(_: argparse.Namespace) -> int:
    settings = load_settings()
    notifier = TelegramNotifier.from_settings(settings)
    if not notifier.enabled():
        print('[WARN] Telegram is not enabled or configured')
        return 0
    notifier.send('[TEST] AICU Factory telegram test')
    print('[OK] Telegram test sent')
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    settings = load_settings()
    job = get_job(settings.db_path, args.job_id)
    if not job:
        print('[ERR] Job not found')
        return 1
    print(json.dumps(job.__dict__, indent=2, ensure_ascii=False))
    return 0


def cmd_z_init_project(args: argparse.Namespace) -> int:
    settings = load_settings()
    ensure_workspace(settings)
    info = scaffold_project(settings.workspace, args.project_name)
    print('[OK] Z project scaffolded')
    print(json.dumps(info, indent=2))
    return 0


def cmd_z_validate(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    payload = json.loads(manifest_path.read_text(encoding='utf-8'))
    if args.preset:
        manifest = load_manifest(manifest_path, preset_name=args.preset)
        payload = manifest.payload
    errors = validate_manifest(payload)
    if errors:
        print('[ERR] Manifest validation failed')
        for err in errors:
            print(f'- {err}')
        return 1
    print(f'[OK] Manifest valid: {manifest_path}')
    if args.preset:
        print(f'[OK] Preset applied: {args.preset}')
    return 0


def cmd_z_run(args: argparse.Namespace) -> int:
    settings = load_settings()
    ensure_workspace(settings)
    manifest = load_manifest(Path(args.manifest), preset_name=args.preset)
    errors = validate_manifest(manifest.payload)
    if errors:
        print('[ERR] Manifest validation failed')
        for err in errors:
            print(f'- {err}')
        return 1
    run_dir = execute_manifest(manifest, settings.workspace)
    print(f'[OK] Z manifest executed: {run_dir}')
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='aicu', description='AICU Factory OSS CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    p = sub.add_parser('init')
    p.set_defaults(func=cmd_init)

    p = sub.add_parser('add-demo')
    p.set_defaults(func=cmd_add_demo)

    p = sub.add_parser('add-script')
    p.add_argument('--name', required=True)
    p.add_argument('--line', default='research')
    p.add_argument('--script', required=True)
    p.add_argument('--output-name', default='script_output.json')
    p.add_argument('--cost-hint', type=float, default=0.02)
    p.add_argument('script_args', nargs='*')
    p.set_defaults(func=cmd_add_script)

    p = sub.add_parser('list')
    p.set_defaults(func=cmd_list)

    p = sub.add_parser('status')
    p.set_defaults(func=cmd_status)

    p = sub.add_parser('list-pipelines')
    p.set_defaults(func=cmd_list_pipelines)

    p = sub.add_parser('list-presets')
    p.set_defaults(func=cmd_list_presets)

    p = sub.add_parser('run')
    p.set_defaults(func=cmd_run)

    p = sub.add_parser('show')
    p.add_argument('job_id')
    p.set_defaults(func=cmd_show)

    p = sub.add_parser('z-init-project')
    p.add_argument('project_name')
    p.set_defaults(func=cmd_z_init_project)

    p = sub.add_parser('z-validate')
    p.add_argument('manifest')
    p.add_argument('--preset', default=None)
    p.set_defaults(func=cmd_z_validate)

    p = sub.add_parser('z-run')
    p.add_argument('manifest')
    p.add_argument('--preset', default=None)
    p.set_defaults(func=cmd_z_run)

    for name, func in [('pause', cmd_pause), ('resume', cmd_resume), ('cancel', cmd_cancel), ('retry', cmd_retry)]:
        p = sub.add_parser(name)
        p.add_argument('job_id')
        p.set_defaults(func=func)

    p = sub.add_parser('test-telegram')
    p.set_defaults(func=cmd_test_telegram)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
