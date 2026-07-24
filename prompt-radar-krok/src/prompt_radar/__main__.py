from __future__ import annotations

import argparse
import json
import sys

from .external_evaluation import evaluate_external
from .pipeline import run_pipeline, validate_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Prompt Radar offline batch")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "smoke"):
        command = subparsers.add_parser(name)
        command.add_argument("--input", required=True, help="Path to the source XLSX")
        command.add_argument("--output", default="artifacts/latest")
        command.add_argument("--skip-100k", action="store_true")
    external = subparsers.add_parser("evaluate-external")
    external.add_argument("--input", required=True, help="Opaque challenge JSONL")
    external.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "evaluate-external":
        result = evaluate_external(args.input, args.output)
        print(
            json.dumps(
                {
                    "output": args.output,
                    "records": result["manifest"]["records"],
                    "gate_failures": result["gate_failures"],
                    "passed": result["passed"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if result["passed"] else 1
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
