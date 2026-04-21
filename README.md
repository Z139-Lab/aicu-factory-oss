\# AICU Factory OSS



Local-first orchestration core for AI experiments, multi-agent workflows, and reproducible research pipelines.



\## Features

\- Job queue

\- Worker execution

\- Pipeline registry

\- Z-Orchestrator presets

\- Cost guard

\- Artifact generation



\## Quick Start

```bash

python -m venv .venv

.\\.venv\\Scripts\\activate

pip install -r requirements.txt

copy .env.example .env

python -m aicu\_factory.cli init

python -m aicu\_factory.cli add-demo

python -m aicu\_factory.cli run

Relation

This repository is part of a broader bounded-criticality research ecosystem, including reproducible experiment and paper packages.

License

MIT


