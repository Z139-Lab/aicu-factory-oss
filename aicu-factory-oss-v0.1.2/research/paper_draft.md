# Research Alignment Draft

## Working title
Bounded Criticality in Multi-Agent AI Systems: Reproducible Orchestration, Cascade Measurements, and Structured Experiment Manifests

## Abstract
AICU Factory OSS provides a local-first orchestration layer for reproducible AI experiments, multi-agent workflows, and artifact generation. The system is designed to support controlled stress sweeps, topology comparisons, report generation, and structured run manifests via an integrated Z-Orchestrator scaffold. The intended research use case is the measurement of collapse probability, cascade size, cost, and execution traces under varying control parameters. By formalizing queueing, worker execution, pipeline registration, safety boundaries, and dataset export, the framework helps transform ad hoc prompt experiments into reproducible computational studies.

## Research-facing components
- Queue + worker execution for controlled batch runs
- Pipeline registry for repeatable experiment classes
- Preset loader for baseline, safe_scan, and paper_mode execution
- Cost guard for bounded runs
- Dataset export and validation for downstream analysis
- Z-Orchestrator manifests for structured protocols and run layouts

## Intended measurements
- Stress parameter
- Collapse probability
- Cascade size
- Failure modes
- Runtime / latency
- Estimated API cost
- Topology and memory configuration metadata

## Reproducibility notes
This repository is structured so that manifests, artifacts, summaries, and exported datasets can be versioned together. The design goal is to support paper-grade experiment packaging once exact task definitions and measurement protocols are locked.

## Suggested paper structure
1. Introduction
2. System Design
3. Experimental Protocol
4. Metrics and Artifact Tracking
5. Results
6. Limitations
7. Reproducibility Package
