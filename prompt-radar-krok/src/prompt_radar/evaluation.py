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
        evaluated_labels = []
        axis_tp = axis_fp = axis_fn = 0
        for label in labels:
            tp = fp = fn = 0
            for record in records:
                expected = set(record.expected_labels.get(axis, []))
                predicted = set(by_id[record.request_id].labels.get(axis, []))
                tp += int(label in expected and label in predicted)
                fp += int(label not in expected and label in predicted)
                fn += int(label in expected and label not in predicted)
            if tp + fp + fn == 0:
                continue
            precision = tp / (tp + fp) if tp + fp else 0.0
            recall = tp / (tp + fn) if tp + fn else 0.0
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
            per_label.append(f1)
            evaluated_labels.append(label)
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
            "macro_f1": round(sum(per_label) / len(per_label), 4) if per_label else 0.0,
            "micro_f1": round(micro_f1, 4),
            "evaluated_labels": evaluated_labels,
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
        "evaluation_uses_split_for_selection": False,
        "passed": not exact
        and not near
        and not any(item.source_topic_id == SEALED_SOURCE_TOPIC for item in dev),
    }


def grouping_metrics(
    records: list[RequestRecord],
    analyses: list[AnalysisRecord],
    emerging_clusters: list[list[str]],
) -> dict[str, object]:
    sealed_ids = {item.request_id for item in records if item.split == "test"}
    cluster_sets = [set(cluster) for cluster in emerging_clusters]
    true_clusters = [
        cluster for cluster in cluster_sets
        if cluster and cluster <= sealed_ids
    ]
    false_clusters = [
        cluster for cluster in cluster_sets
        if cluster and not cluster.intersection(sealed_ids)
    ]
    mixed_clusters = [
        cluster for cluster in cluster_sets
        if cluster.intersection(sealed_ids) and not cluster <= sealed_ids
    ]
    novelty_precision = (
        len(true_clusters) / len(cluster_sets) if cluster_sets else 0.0
    )

    predicted_group: dict[str, str] = {
        request_id: f"singleton:{request_id}" for request_id in sealed_ids
    }
    for cluster_index, cluster in enumerate(cluster_sets):
        for request_id in cluster & sealed_ids:
            predicted_group[request_id] = f"cluster:{cluster_index}"

    sealed_list = sorted(sealed_ids)
    true_pairs = {
        (left, right)
        for index, left in enumerate(sealed_list)
        for right in sealed_list[index + 1 :]
    }
    predicted_pairs = {
        (left, right)
        for index, left in enumerate(sealed_list)
        for right in sealed_list[index + 1 :]
        if predicted_group[left] == predicted_group[right]
    }
    pair_tp = len(true_pairs & predicted_pairs)
    pair_precision = pair_tp / len(predicted_pairs) if predicted_pairs else 0.0
    pair_recall = pair_tp / len(true_pairs) if true_pairs else 0.0
    pair_f1 = (
        2 * pair_precision * pair_recall / (pair_precision + pair_recall)
        if pair_precision + pair_recall
        else 0.0
    )

    group_sizes = Counter(predicted_group.values())
    bcubed_precision = 1.0 if sealed_ids else 0.0
    bcubed_recall = (
        sum(group_sizes[predicted_group[item]] / len(sealed_ids) for item in sealed_ids)
        / len(sealed_ids)
        if sealed_ids
        else 0.0
    )
    bcubed_f1 = (
        2 * bcubed_precision * bcubed_recall / (bcubed_precision + bcubed_recall)
        if bcubed_precision + bcubed_recall
        else 0.0
    )
    ari = 1.0 if len(set(predicted_group.values())) <= 1 and sealed_ids else 0.0
    known = [item for item in analyses if item.scenario_status == "known"]
    residual = [item for item in analyses if item.scenario_status == "unresolved"]
    return {
        "sealed_pairwise_f1": round(pair_f1, 4),
        "sealed_bcubed_f1": round(bcubed_f1, 4),
        "sealed_ari": round(ari, 4),
        "novelty_precision": round(novelty_precision, 4),
        "known_requests": len(known),
        "unresolved_rate_after_discovery": round(
            len(residual) / len(analyses), 4
        ) if analyses else 0.0,
        "known_only_false_emerging": len(false_clusters),
        "mixed_emerging_clusters": len(mixed_clusters),
        "sealed_members_recovered": sum(
            len(cluster & sealed_ids) for cluster in cluster_sets
        ),
        "sealed_members_total": len(sealed_ids),
        "scope_note": "Grouping score is limited to the sealed synthetic challenge.",
    }
