from __future__ import annotations

from .config import (
    ABSTAIN_THRESHOLD,
    INTENT_KEYWORDS,
    KNOWN_MATCH_THRESHOLD,
    KNOWN_USE_CASES,
    OBJECT_KEYWORDS,
    SYSTEM_KEYWORDS,
)
from .vector import normalize, similarity


def _score_keywords(text: str, mapping: dict[str, tuple[str, ...]]) -> tuple[list[str], float, list[str]]:
    normalized = normalize(text)
    hits: list[tuple[str, int, list[str]]] = []
    for label, keywords in mapping.items():
        matched = sorted({keyword for keyword in keywords if keyword in normalized})
        if matched:
            hits.append((label, len(matched), matched))
    hits.sort(key=lambda item: (-item[1], item[0]))
    if not hits:
        return [], 0.0, []
    best = hits[0][1]
    labels = [label for label, score, _ in hits if score >= max(1, best - 1)]
    evidence = [word for _, score, words in hits if score >= max(1, best - 1) for word in words][:8]
    confidence = min(0.98, 0.58 + 0.12 * best + 0.04 * min(2, len(labels) - 1))
    return labels, confidence, evidence


def classify(text: str) -> tuple[dict[str, list[str]], dict[str, float], list[str], dict[str, list[str]]]:
    systems, system_conf, system_evidence = _score_keywords(text, SYSTEM_KEYWORDS)
    intents, intent_conf, intent_evidence = _score_keywords(text, INTENT_KEYWORDS)
    objects, object_conf, object_evidence = _score_keywords(text, OBJECT_KEYWORDS)
    normalized = normalize(text)
    if "без ответа" in normalized and "reply" in intents:
        intents.remove("reply")

    if any(word in normalized for word in ("еженедель", "периодич", "регуляр", "каждый")):
        mode = ["recurring"]
    elif any(word in normalized for word in ("монитор", "отслеж", "контрол")):
        mode = ["monitoring"]
    elif any(word in normalized for word in ("уведом", "напомин", "подсвеч")):
        mode = ["notification"]
    else:
        mode = ["one_shot"]

    if any(system in systems for system in ("CRM",)) or any(word in normalized for word in ("клиент", "тендер", "продаж")):
        domain = ["sales"]
    elif any(system in systems for system in ("Jira", "ISUP", "Project")) or "задач" in normalized:
        domain = ["projects"]
    elif any(word in normalized for word in ("сотрудник", "руководител", "feedback", "анкетирован")):
        domain = ["HR"]
    elif any(system in systems for system in ("Confluence", "OpenWeb")):
        domain = ["knowledge"]
    else:
        domain = ["productivity"]

    labels = {
        "system": systems,
        "intent": intents,
        "object": objects[:2],
        "automation_mode": mode,
        "business_domain": domain,
    }
    confidences = {
        "system": system_conf,
        "intent": intent_conf,
        "object": object_conf,
        "automation_mode": 0.82,
        "business_domain": 0.78,
    }
    evidence = {
        "system": system_evidence,
        "intent": intent_evidence,
        "object": object_evidence,
        "automation_mode": mode,
        "business_domain": domain,
    }
    abstain = [axis for axis, value in confidences.items() if value < ABSTAIN_THRESHOLD]
    for axis in abstain:
        labels[axis] = []
    return labels, confidences, abstain, evidence


def known_match(text: str, labels: dict[str, list[str]]) -> tuple[str | None, float]:
    best_id: str | None = None
    best_score = 0.0
    request_systems = set(labels.get("system", []))
    request_intents = set(labels.get("intent", []))
    for candidate in KNOWN_USE_CASES:
        system_overlap = bool(request_systems.intersection(candidate["systems"]))
        intent_overlap = bool(request_intents.intersection(candidate["intents"]))
        if not system_overlap or not intent_overlap:
            continue
        semantic = similarity(text, candidate["prototype"])
        score = 0.55 * semantic + 0.25 + 0.20 * min(
            1.0, len(request_systems.intersection(candidate["systems"]))
        )
        if score > best_score:
            best_id, best_score = candidate["scenario_id"], score
    if best_score < KNOWN_MATCH_THRESHOLD:
        return None, best_score
    return best_id, min(0.99, best_score)
