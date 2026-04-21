from __future__ import annotations

import argparse
import json
from pathlib import Path


def export_dataset(input_path: Path, output_path: Path) -> None:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    dataset = {
        "experiment_id": raw.get("experiment_id", "demo_experiment"),
        "model": raw.get("model", "unknown-model"),
        "topology": raw.get("topology", "unknown"),
        "stress": raw.get("stress", 0.0),
        "runs": raw.get("runs", 0),
        "collapse_prob": raw.get("collapse_prob", 0.0),
        "cascade_size_mean": raw.get("cascade_size_mean", 0.0),
        "cascade_size_std": raw.get("cascade_size_std", 0.0),
        "ci_95": raw.get("ci_95", [0.0, 0.0]),
        "config": raw.get("config", {}),
        "environment": raw.get("environment", {}),
        "validity": raw.get("validity", {"quality_flag": "UNKNOWN"}),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export_dataset(Path(args.input), Path(args.output))
    print(f"[OK] Dataset exported to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
