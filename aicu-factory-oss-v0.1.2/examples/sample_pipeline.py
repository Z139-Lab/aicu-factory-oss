from __future__ import annotations

import json
from datetime import datetime, UTC


def main() -> int:
    payload = {
        "experiment_id": "sample_pipeline_run",
        "model": "demo-model",
        "topology": "dag",
        "stress": 0.93,
        "runs": 40,
        "collapse_prob": 0.25,
        "cascade_size_mean": 0.41,
        "cascade_size_std": 0.12,
        "ci_95": [0.18, 0.33],
        "config": {
            "memory_alpha": 0.6,
            "retry_limit": 3,
        },
        "environment": {
            "timestamp": datetime.now(UTC).isoformat(),
            "sdk_version": "aicu-factory-oss-0.1.0",
        },
        "validity": {
            "quality_flag": "OK",
            "failed_runs": 0,
        },
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
