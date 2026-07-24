from __future__ import annotations

import argparse
import json
import sys

from .pipeline import run_pipeline, validate_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Prompt Radar offline batch")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "smoke"):
        command = subparsers.add_parser(name)
        command.add_argument("--input", required=True, help="Path to the source XLSX")
        command.add_argument("--output", default="artifacts/latest")
        command.add_argument("--skip-100k", action="store_true")
    args = parser.parse_args()
    summary = run_pipeline(args.input, args.output, include_100k=not args.skip_100k)
    failures = validate_summary(summary) if args.command == "smoke" else []
    print(
        json.dumps(
            {
                "output": args.output,
                "run_fingerprint": summary["manifest"]["run_fingerprint"],
                "passport_status": summary["passport"]["status"],
                "failures": failures,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
