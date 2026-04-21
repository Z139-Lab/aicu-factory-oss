from __future__ import annotations

import argparse
from pathlib import Path

import requests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--endpoint", required=True)
    args = parser.parse_args()
    payload = Path(args.path).read_text(encoding="utf-8")
    response = requests.post(args.endpoint, data=payload.encode("utf-8"), headers={"Content-Type": "application/json"}, timeout=20)
    response.raise_for_status()
    print("[OK] Upload completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
