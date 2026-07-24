from __future__ import annotations

import random
import hashlib
from collections import Counter, defaultdict
from dataclasses import asdict

from .config import KNOWN_USE_CASES, RESIDUAL_SIMILARITY_THRESHOLD, SEED
from .contracts import AnalysisRecord, RequestRecord
from .vector import similarity


def _signature(analysis: AnalysisRecord) -> tuple[str, str]:
    systems = analysis.labels.get("system", [])
    domain = analysis.labels.get("business_domain", ["unknown"])
    return ("+".join(sorted(systems)) or "unknown", domain[0] if domain else "unknown")


def cluster_residuals(
    records: list[RequestRecord],
    analyses: list[AnalysisRecord],
    allowed_groups: set[str] | None = None,
) -> list[list[int]]:
    record_by_id = {record.request_id: record for record in records}
    residual = [
        index
        for index, analysis in enumerate(analyses)
        if analysis.scenario_status == "unresolved"
        and analysis.redaction_status == "passed"
        and (
            allowed_groups is None
            or record_by_id[analysis.request_id].canonical_group_id in allowed_groups
        )
    ]
    parent = {index: index for index in residual}

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for offset, left in enumerate(residual):
        for right in residual[offset + 1 :]:
            if _signature(analyses[left]) != _signature(analyses[right]):
                continue
            if similarity(analyses[left].redacted_text, analyses[right].redacted_text) >= RESIDUAL_SIMILARITY_THRESHOLD:
                union(left, right)
    groups: dict[int, list[int]] = defaultdict(list)
    for index in residual:
        groups[find(index)].append(index)
    return sorted(groups.values(), key=lambda group: (-len(group), group[0]))


def stability_report(
    records: list[RequestRecord],
    analyses: list[AnalysisRecord],
    base_cluster: list[int],
    runs: int = 10,
) -> dict[str, object]:
    record_by_id = {record.request_id: record for record in records}
    base_ids = {analyses[index].request_id for index in base_cluster}
    base_groups = {
        record_by_id[request_id].canonical_group_id for request_id in base_ids
    }
    jaccards: list[float] = []
    inclusion: Counter[str] = Counter()
    details = []
    for run in range(runs):
        rng = random.Random(SEED + run)
        sample_size = max(2, round(len(base_groups) * 0.85))
        selected_groups = set(rng.sample(sorted(base_groups), min(sample_size, len(base_groups))))
        candidates = cluster_residuals(records, analyses, selected_groups)
        aligned = max(
            candidates,
            key=lambda cluster: len({analyses[index].request_id for index in cluster} & base_ids),
            default=[],
        )
        aligned_ids = {analyses[index].request_id for index in aligned}
        union_ids = base_ids | aligned_ids
        jaccard = len(base_ids & aligned_ids) / len(union_ids) if union_ids else 1.0
        jaccards.append(jaccard)
        inclusion.update(aligned_ids)
        details.append({"run": run + 1, "selected_groups": len(selected_groups), "jaccard": round(jaccard, 4)})
    core = sorted(request_id for request_id, count in inclusion.items() if count / runs >= 0.7)
    return {
        "perturbation_runs": runs,
        "mean_jaccard": round(sum(jaccards) / len(jaccards), 4),
        "core_jaccard": round(min(jaccards), 4),
        "core_members": core,
        "details": details,
    }


def build_passport(
    records: list[RequestRecord],
    analyses: list[AnalysisRecord],
    cluster: list[int],
    stability: dict[str, object],
) -> dict[str, object]:
    record_by_id = {record.request_id: record for record in records}
    members = [analyses[index] for index in cluster]
    group_count = len({record_by_id[item.request_id].canonical_group_id for item in members})
    similarities = [
        similarity(left.redacted_text, right.redacted_text)
        for pos, left in enumerate(members)
        for right in members[pos + 1 :]
    ]
    cohesion = sum(similarities) / len(similarities) if similarities else 1.0
    systems = Counter(value for item in members for value in item.labels.get("system", []))
    intents = Counter(value for item in members for value in item.labels.get("intent", []))
    status = (
        "emerging"
        if group_count >= 4
        and cohesion >= 0.25
        and float(stability["mean_jaccard"]) >= 0.75
        and all(
            "system" not in item.abstain_axes
            and "business_domain" not in item.abstain_axes
            for item in members
        )
        else "unresolved"
    )
    member_ids = sorted(item.request_id for item in members)
    scenario_id = "residual-" + hashlib.sha256(
        "|".join(member_ids).encode("utf-8")
    ).hexdigest()[:12]
    top_systems = [
        label for label, _ in sorted(systems.items(), key=lambda item: (-item[1], item[0]))
    ][:2]
    top_intents = [
        label for label, _ in sorted(intents.items(), key=lambda item: (-item[1], item[0]))
    ][:2]
    system_name = " + ".join(top_systems) if top_systems else "Неопределённая система"
    intent_name = " + ".join(top_intents) if top_intents else "неопределённое действие"
    nearest_known_similarity = max(
        (
            similarity(member.redacted_text, candidate["prototype"])
            for member in members
            for candidate in KNOWN_USE_CASES
        ),
        default=0.0,
    )
    examples = [item.redacted_text[:240] for item in members[:3]]
    return {
        "scenario_id": scenario_id,
        "name": f"{system_name} → {intent_name}",
        "status": status,
        "summary": (
            f"{group_count} независимых формулировок объединяют "
            f"{system_name} и действие {intent_name}. "
            "Название извлечено только из redacted evidence."
        ),
        "naming_method": "extractive",
        "support_requests": len(members),
        "support_canonical_groups": group_count,
        "cohesion": round(cohesion, 4),
        "distinctness": round(max(0.0, 1.0 - nearest_known_similarity), 4),
        "stability": stability,
        "systems": dict(systems),
        "intents": dict(intents),
        "examples": examples,
        "evidence_ids": [item.request_id for item in members[:3]],
        "synthetic_flag": all(record_by_id[item.request_id].synthetic_flag for item in members),
        "sealed_challenge": bool(members) and all(
            record_by_id[item.request_id].split == "test" for item in members
        ),
        "action": "VALIDATE",
        "action_rule": "E0 and synthetic evidence prohibit SCALE/AUTOMATE.",
        "dynamics": "N/A: synthetic timestamps are not business evidence",
        "failure_signal": "N/A: no real response/error/feedback telemetry",
    }


def analyses_as_dicts(analyses: list[AnalysisRecord]) -> list[dict[str, object]]:
    return [asdict(item) for item in analyses]
