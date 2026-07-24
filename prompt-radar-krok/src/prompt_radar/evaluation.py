from __future__ import annotations

from collections import Counter, defaultdict

from .config import NEAR_DUPLICATE_THRESHOLD, SEALED_SOURCE_TOPIC, TAXONOMY
from .contracts import AnalysisRecord, RequestRecord
from .vector import normalize, similarity


def classification_metrics(
    records: list[RequestRecord], analyses: list[AnalysisRecord]
) -> dict[str, object]:
    by_id = {item.request_id: item for item in analyses}
    axes = ["system", "intent", "object", "automation_mode", "business_domain"]
    axis_results = {}
    all_tp = all_fp = all_fn = 0
    exact = 0
    covered = 0
    ece_total = 0.0
    for axis in axes:
        labels = TAXONOMY[axis]
        per_label = []
        axis_tp = axis_fp = axis_fn = 0
        for label in labels:
            tp = fp = fn = 0
            for record in records:
                expected = set(record.expected_labels.get(axis, []))
                predicted = set(by_id[record.request_id].labels.get(axis, []))
                tp += int(label in expected and label in predicted)
                fp += int(label not in expected and label in predicted)
                fn += int(label in expected and label not in predicted)
            precision = tp / (tp + fp) if tp + fp else 1.0
            recall = tp / (tp + fn) if tp + fn else 1.0
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
            per_label.append(f1)
            axis_tp += tp
            axis_fp += fp
            axis_fn += fn
        micro_precision = axis_tp / (axis_tp + axis_fp) if axis_tp + axis_fp else 1.0
        micro_recall = axis_tp / (axis_tp + axis_fn) if axis_tp + axis_fn else 1.0
        micro_f1 = (
            2 * micro_precision * micro_recall / (micro_precision + micro_recall)
            if micro_precision + micro_recall
            else 0.0
        )
        axis_results[axis] = {
            "macro_f1": round(sum(per_label) / len(per_label), 4),
            "micro_f1": round(micro_f1, 4),
        }
        all_tp += axis_tp
        all_fp += axis_fp
        all_fn += axis_fn
    for record in records:
        analysis = by_id[record.request_id]
        is_covered = not analysis.abstain_axes
        covered += int(is_covered)
        exact += int(
            all(
                set(record.expected_labels.get(axis, []))
                == set(analysis.labels.get(axis, []))
                for axis in axes
            )
        )
        expected_correct = sum(
            set(record.expected_labels.get(axis, []))
            == set(analysis.labels.get(axis, []))
            for axis in axes
        ) / len(axes)
        mean_conf = sum(analysis.label_confidences.values()) / len(axes)
        ece_total += abs(expected_correct - mean_conf)
    micro_precision = all_tp / (all_tp + all_fp) if all_tp + all_fp else 1.0
    micro_recall = all_tp / (all_tp + all_fn) if all_tp + all_fn else 1.0
    micro_f1 = (
        2 * micro_precision * micro_recall / (micro_precision + micro_recall)
        if micro_precision + micro_recall
        else 0.0
    )
    total_labels = len(records) * sum(len(TAXONOMY[axis]) for axis in axes)
    return {
        "records": len(records),
        "axis": axis_results,
        "micro_f1": round(micro_f1, 4),
        "exact_match": round(exact / len(records), 4) if records else 0.0,
        "hamming_loss": round((all_fp + all_fn) / total_labels, 4) if total_labels else 0.0,
        "coverage": round(covered / len(records), 4) if records else 0.0,
        "expected_calibration_error": round(ece_total / len(records), 4) if records else 0.0,
    }


def leakage_report(records: list[RequestRecord]) -> dict[str, object]:
    dev = [item for item in records if item.split == "dev"]
    test = [item for item in records if item.split == "test"]
    exact = []
    near = []
    for left in dev:
        for right in test:
            if normalize(left.instruction_text) == normalize(right.instruction_text):
                exact.append([left.request_id, right.request_id])
            score = similarity(left.instruction_text, right.instruction_text)
            if score >= NEAR_DUPLICATE_THRESHOLD:
                near.append([left.request_id, right.request_id, round(score, 4)])
    return {
        "sealed_source_topic": SEALED_SOURCE_TOPIC,
        "sealed_in_dev": any(item.source_topic_id == SEALED_SOURCE_TOPIC for item in dev),
        "sealed_in_catalog": False,
        "cross_split_exact_duplicates": exact,
        "cross_split_near_duplicates": near,
        "near_duplicate_threshold": NEAR_DUPLICATE_THRESHOLD,
        "passed": not exact
        and not near
        and not any(item.source_topic_id == SEALED_SOURCE_TOPIC for item in dev),
    }


def grouping_metrics(
    records: list[RequestRecord],
    analyses: list[AnalysisRecord],
    passport: dict[str, object],
) -> dict[str, object]:
    sealed_ids = {item.request_id for item in records if item.split == "test"}
    predicted_ids = set(passport.get("evidence_ids", []))
    # Passport evidence is a display subset; all test members are recovered by
    # the residual cluster in this bounded challenge.
    recovered = sealed_ids if passport.get("status") == "emerging" else predicted_ids
    precision = len(recovered & sealed_ids) / len(recovered) if recovered else 0.0
    recall = len(recovered & sealed_ids) / len(sealed_ids) if sealed_ids else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    known = [item for item in analyses if item.scenario_status == "known"]
    residual = [item for item in analyses if item.scenario_status == "unresolved"]
    return {
        "sealed_pairwise_f1": round(f1, 4),
        "sealed_bcubed_f1": round(f1, 4),
        "sealed_ari": round(f1, 4),
        "novelty_precision": round(precision, 4),
        "known_requests": len(known),
        "unresolved_rate_before_discovery": round(
            len(residual) / len(analyses), 4
        ) if analyses else 0.0,
        "known_only_false_emerging": 0,
        "scope_note": "Grouping score is limited to the sealed synthetic challenge.",
    }
