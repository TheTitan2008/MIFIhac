from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RequestRecord:
    request_id: str
    run_id: str
    instruction_text: str
    dataset_kind: str
    synthetic_flag: bool
    source_topic_id: str
    canonical_group_id: str
    template_family_id: str
    split: str
    dataset_version: str
    expected_labels: dict[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalysisRecord:
    request_id: str
    redacted_text: str
    redaction_status: str
    pii_redaction_count: int
    prompt_injection_flag: bool
    labels: dict[str, list[str]]
    label_confidences: dict[str, float]
    abstain_axes: list[str]
    evidence: dict[str, list[str]]
    scenario_id: str
    scenario_status: str
    membership_confidence: float
    quality_risk: bool
    metadata: dict[str, Any] = field(default_factory=dict)
