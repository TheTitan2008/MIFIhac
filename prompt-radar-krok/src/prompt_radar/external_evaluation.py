from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .config import (
    ABSTAIN_THRESHOLD,
    ALGORITHM_VERSION,
    SCHEMA_VERSION,
    SEED,
    TAXONOMY_VERSION,
)
from .contracts import AnalysisRecord, RequestRecord
from .evaluation import classification_metrics
from .message_parser import ALL_AXES, parse_openai_payload, persisted_message_record
from .pipeline import analyze

EXTERNAL_SCHEMA_VERSION = "openai-message-challenge-v1"
EXTERNAL_GATES = {
    "minimum_coverage": 0.50,
    "minimum_key_axis_macro_f1": 0.70,
    "key_axes": ["system", "intent", "object"],
}


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _quarantined_analysis(parsed: dict[str, object]) -> AnalysisRecord:
    return AnalysisRecord(
        request_id=str(parsed["request_id"]),
        redacted_text="",
        redaction_status="quarantine",
        pii_redaction_count=int(parsed.get("pii_redaction_count") or 0),
        prompt_injection_flag=bool(parsed.get("prompt_injection_flag")),
        labels={axis: [] for axis in ALL_AXES},
        label_confidences={axis: 0.0 for axis in ALL_AXES},
        abstain_axes=list(ALL_AXES),
        evidence={},
        scenario_id="quarantine",
        scenario_status="unresolved",
        membership_confidence=0.0,
        quality_risk=True,
        metadata={"parse_error": parsed.get("parse_error")},
    )


def evaluate_external(input_jsonl: str | Path, output_dir: str | Path) -> dict[str, object]:
    source = Path(input_jsonl).resolve()
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    with source.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("expected_labels"), dict):
                raise ValueError(
                    f"Line {line_number}: expected_labels object is required"
                )
            rows.append(row)
    if not rows:
        raise ValueError("External challenge is empty")

    parsed_rows = []
    records = []
    for index, row in enumerate(rows, start=1):
        payload = row.get("payload")
        if payload is None:
            payload = {
                key: value
                for key, value in row.items()
                if key not in {"request_id", "expected_labels", "synthetic_flag"}
            }
        request_id = str(row.get("request_id") or f"external-{index:06d}")
        parsed = parse_openai_payload(payload, request_id=request_id)
        parsed_rows.append(parsed)
        records.append(
            RequestRecord(
                request_id=request_id,
                run_id=f"external-run-{request_id}",
                instruction_text=str(parsed.get("current_user_goal") or ""),
                dataset_kind="external_opaque_challenge",
                synthetic_flag=bool(row.get("synthetic_flag", False)),
                source_topic_id="external",
                canonical_group_id=request_id,
                template_family_id=request_id,
                split="external",
                dataset_version=EXTERNAL_SCHEMA_VERSION,
                expected_labels=row["expected_labels"],
            )
        )

    analyses = analyze(records)
    analyses = [
        _quarantined_analysis(parsed)
        if parsed["redaction_status"] == "quarantine"
        else analysis
        for parsed, analysis in zip(parsed_rows, analyses, strict=True)
    ]
    metrics = classification_metrics(records, analyses)
    gate_failures = []
    if metrics["coverage"] < EXTERNAL_GATES["minimum_coverage"]:
        gate_failures.append("coverage")
    for axis in EXTERNAL_GATES["key_axes"]:
        if (
            metrics["axis"][axis]["macro_f1"]
            < EXTERNAL_GATES["minimum_key_axis_macro_f1"]
        ):
            gate_failures.append(f"{axis}-macro-f1")

    source_hashes = {
        path.name: _sha256(path.read_bytes())
        for path in sorted(Path(__file__).parent.glob("*.py"))
    }
    frozen_config = {
        "schema_version": SCHEMA_VERSION,
        "external_schema_version": EXTERNAL_SCHEMA_VERSION,
        "taxonomy_version": TAXONOMY_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "seed": SEED,
        "abstain_threshold": ABSTAIN_THRESHOLD,
        "gates": EXTERNAL_GATES,
        "source_hashes": source_hashes,
    }
    manifest = {
        **frozen_config,
        "input_sha256": _sha256(source.read_bytes()),
        "config_sha256": _sha256(_canonical_json(frozen_config).encode("utf-8")),
        "external_network_calls": 0,
        "records": len(records),
        "quarantined_records": sum(
            parsed["redaction_status"] == "quarantine" for parsed in parsed_rows
        ),
    }
    result = {
        "label": "EXTERNAL OPAQUE EVALUATION / NO TUNING",
        "metrics": metrics,
        "gate_failures": gate_failures,
        "passed": not gate_failures,
        "manifest": manifest,
    }
    (destination / "evaluation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (destination / "parsed_requests.jsonl").open("w", encoding="utf-8") as stream:
        for parsed, analysis in zip(parsed_rows, analyses, strict=True):
            row = {
                **persisted_message_record(parsed),
                "labels": analysis.labels,
                "label_confidences": analysis.label_confidences,
                "scenario_id": analysis.scenario_id,
                "scenario_status": analysis.scenario_status,
            }
            stream.write(_canonical_json(row) + "\n")
    return result
