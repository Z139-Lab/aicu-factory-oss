# AICU Factory OSS

AICU Factory OSS is a local-first orchestration core for AI experiments, multi-agent cascade workflows, and reproducible research pipelines.

It provides a lightweight execution layer built around:

- job queue management
- background workers
- pipeline registry
- artifact generation
- experiment presets
- safety / cost boundaries

## What is this?

This repository is the open-source core of the AICU workflow system.

It is designed for researchers and builders who want to run structured AI or multi-agent experiments, generate reports and artifacts, and keep execution reproducible.

## Key Features

- SQLite-backed local job queue
- Worker-based execution
- Pipeline registry for sweeps, reports, figures, and scripts
- Z-Orchestrator-style presets and manifests
- Cost guard / safety boundaries
- Artifact outputs for reports, summaries, and datasets

## Quick Start

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

python -m aicu_factory.cli init
python -m aicu_factory.cli add-demo
python -m aicu_factory.cli run
Relation to the research ecosystem

AICU Factory OSS is part of a broader bounded-criticality research ecosystem.

It complements repositories focused on:

bounded criticality experiments
UVP / criticality analysis frameworks
power-grid case studies
paper-facing reproducibility packages
Intended Use

This repository is intended for:

experiment orchestration
multi-agent cascade workflow control
reproducible report generation
structured local research pipelines
License

MIT


然後：

```powershell
git add README.md
git commit -m "Expand README with purpose, quick start, and research relation"
git push