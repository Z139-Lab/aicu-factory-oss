from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_KEYS = {
    "experiment_id",
    "model",
    "topology",
    "stress",
    "runs",
    "collapse_prob",
    "cascade_size_mean",
    "cascade_size_std",
    "ci_95",
    "config",
    "environment",
    "validity",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_KEYS - set(payload.keys()))
    if missing:
        print("[ERR] Missing keys:", ", ".join(missing))
        return 1
    print("[OK] Dataset shape looks valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
