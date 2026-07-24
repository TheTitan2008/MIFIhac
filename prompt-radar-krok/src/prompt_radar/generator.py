from __future__ import annotations

import hashlib
import random
from collections.abc import Iterable

from .config import DATASET_VERSION, SEALED_SOURCE_TOPIC, SEED
from .contracts import RequestRecord

PREFIXES = [
    "Нужно выполнить рабочую задачу: ",
    "Сотрудник просит агента: ",
    "Практический запрос: ",
]
SUFFIXES = [
    " Результат должен быть пригоден для проверки.",
    " Нужен понятный итог без выдуманных данных.",
]

SEALED_CHALLENGE = [
    "Разбери новые письма и заведи по ним карточки задач на моей доске Project.",
    "Из входящей почты создай тикеты Project и сохрани связь с исходным письмом.",
    "Перенеси поручения из писем в новые задачи на доске Project.",
    "По непрочитанным письмам сформируй и актуализируй тикеты в Project.",
    "Письма с запросами преврати в задачи Project, не дублируя существующие.",
    "Создай на личной доске Project карточки по полученным рабочим письмам.",
]

TOPIC_GOLD: dict[str, dict[str, list[str]]] = {
    "A3": {"system": ["Email"], "intent": ["summarize"], "object": ["email"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A4": {"system": ["CRM"], "intent": ["search"], "object": ["client", "deal"], "automation_mode": ["one_shot"], "business_domain": ["sales"]},
    "A5": {"system": ["Email"], "intent": ["monitor"], "object": ["email"], "automation_mode": ["recurring", "monitoring"], "business_domain": ["productivity"]},
    "A6": {"system": ["CRM", "Email"], "intent": ["summarize", "notify"], "object": ["deal", "tender"], "automation_mode": ["recurring", "notification"], "business_domain": ["sales"]},
    "A7": {"system": ["CRM"], "intent": ["search"], "object": ["client", "project"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    "A8": {"system": ["OpenWeb"], "intent": ["search", "summarize"], "object": ["client", "document"], "automation_mode": ["one_shot"], "business_domain": ["sales"]},
    "A9": {"system": ["CRM", "Excel"], "intent": ["search", "export"], "object": ["client", "report"], "automation_mode": ["one_shot"], "business_domain": ["sales"]},
    "A10": {"system": ["CoolFeedback"], "intent": ["reply"], "object": ["employee_note"], "automation_mode": ["one_shot"], "business_domain": ["HR"]},
    "A11": {"system": ["Other"], "intent": ["create"], "object": ["employee_note"], "automation_mode": ["one_shot"], "business_domain": ["HR"]},
    "A12": {"system": ["ISUP"], "intent": ["create", "update"], "object": ["task", "project"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    "A13": {"system": ["CRM"], "intent": ["summarize"], "object": ["tender", "report"], "automation_mode": ["recurring"], "business_domain": ["sales"]},
    "A14": {"system": ["Jira"], "intent": ["search"], "object": ["task"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    "A15": {"system": ["Jira"], "intent": ["search"], "object": ["task"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    "A16": {"system": ["Other"], "intent": ["create"], "object": ["employee_note"], "automation_mode": ["one_shot"], "business_domain": ["HR"]},
    "A17": {"system": ["Excel"], "intent": ["export"], "object": ["report"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A18": {"system": ["Excel"], "intent": ["export"], "object": ["report"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A19": {"system": ["OpenWeb"], "intent": ["search"], "object": ["document"], "automation_mode": ["one_shot"], "business_domain": ["knowledge"]},
    "A20": {"system": ["Confluence"], "intent": ["search"], "object": ["document"], "automation_mode": ["one_shot"], "business_domain": ["knowledge"]},
    "A21": {"system": ["Calendar"], "intent": ["search", "schedule"], "object": ["meeting"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A22": {"system": ["Other"], "intent": ["update"], "object": ["task"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    "A23": {"system": ["Other"], "intent": ["create", "update"], "object": ["task"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    "A24": {"system": ["Calendar"], "intent": ["search", "schedule"], "object": ["room", "meeting"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A25": {"system": ["Email"], "intent": ["reply"], "object": ["email"], "automation_mode": ["one_shot"], "business_domain": ["sales"]},
    "A26": {"system": ["Calendar"], "intent": ["create", "summarize"], "object": ["meeting", "employee_note"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A27": {"system": ["CRM"], "intent": ["search"], "object": ["client"], "automation_mode": ["one_shot"], "business_domain": ["sales"]},
    "A28": {"system": ["Calendar"], "intent": ["schedule"], "object": ["meeting"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A29": {"system": ["Calendar"], "intent": ["search"], "object": ["meeting", "document"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A30": {"system": ["Calendar"], "intent": ["create", "notify"], "object": ["task", "meeting"], "automation_mode": ["notification"], "business_domain": ["productivity"]},
    "A31": {"system": ["Calendar"], "intent": ["search"], "object": ["meeting"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    "A32": {"system": ["Email", "Project"], "intent": ["create"], "object": ["email", "task"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    "A33": {"system": ["ISUP"], "intent": ["monitor", "notify"], "object": ["project"], "automation_mode": ["recurring", "monitoring", "notification"], "business_domain": ["projects"]},
}

MANUAL_CHALLENGE: list[tuple[str, dict[str, list[str]]]] = [
    (
        "Подбери общий свободный час для команды и забронируй переговорную.",
        {"system": ["Calendar"], "intent": ["schedule"], "object": ["meeting", "room"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    ),
    (
        "Покажи приоритетные задачи, которые назначены мне в Jira.",
        {"system": ["Jira"], "intent": ["search"], "object": ["task"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    ),
    (
        "Сделай краткий обзор сегодняшней входящей почты.",
        {"system": ["Email"], "intent": ["summarize"], "object": ["email"], "automation_mode": ["one_shot"], "business_domain": ["productivity"]},
    ),
    (
        "Найди регламент процесса в Confluence.",
        {"system": ["Confluence"], "intent": ["search"], "object": ["document"], "automation_mode": ["one_shot"], "business_domain": ["knowledge"]},
    ),
    (
        "Выгрузи сведения о клиенте из CRM в Excel.",
        {"system": ["CRM", "Excel"], "intent": ["export"], "object": ["client", "report"], "automation_mode": ["one_shot"], "business_domain": ["sales"]},
    ),
    (
        "Следи за письмами без ответа и напомни через два часа.",
        {"system": ["Email"], "intent": ["monitor", "notify"], "object": ["email"], "automation_mode": ["monitoring", "notification"], "business_domain": ["productivity"]},
    ),
    (
        "Добавь задачу в ИСУП и обнови её статус.",
        {"system": ["ISUP"], "intent": ["create", "update"], "object": ["task", "project"], "automation_mode": ["one_shot"], "business_domain": ["projects"]},
    ),
    (
        "Собери результаты тендеров за неделю в отчёт.",
        {"system": ["CRM"], "intent": ["summarize"], "object": ["tender", "report"], "automation_mode": ["one_shot"], "business_domain": ["sales"]},
    ),
]


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def generate_records(topics: Iterable[tuple[str, str]], seed: int = SEED) -> list[RequestRecord]:
    rng = random.Random(seed)
    records: list[RequestRecord] = []
    for source_id, topic in topics:
        if source_id == SEALED_SOURCE_TOPIC:
            for index, text in enumerate(SEALED_CHALLENGE, start=1):
                records.append(
                    RequestRecord(
                        request_id=f"sealed-{index:02d}",
                        run_id=f"run-sealed-{index:02d}",
                        instruction_text=text,
                        dataset_kind="synthetic_sealed_challenge",
                        synthetic_flag=True,
                        source_topic_id=source_id,
                        canonical_group_id=f"A32-independent-{index:02d}",
                        template_family_id=f"sealed-manual-{index:02d}",
                        split="test",
                        dataset_version=DATASET_VERSION,
                        expected_labels=TOPIC_GOLD[source_id],
                    )
                )
            continue
        labels = TOPIC_GOLD[source_id]
        for variant in range(2):
            prefix = PREFIXES[(int(source_id[1:]) + variant) % len(PREFIXES)]
            suffix = SUFFIXES[(int(source_id[1:]) + variant) % len(SUFFIXES)]
            text = f"{prefix}{topic}{suffix}"
            request_id = _stable_id(source_id, str(variant), text)
            records.append(
                RequestRecord(
                    request_id=request_id,
                    run_id=f"run-{request_id}",
                    instruction_text=text,
                    dataset_kind="synthetic_dev",
                    synthetic_flag=True,
                    source_topic_id=source_id,
                    canonical_group_id=f"{source_id}-canonical",
                    template_family_id=f"generic-{variant}",
                    split="dev",
                    dataset_version=DATASET_VERSION,
                    expected_labels=labels,
                )
            )
    rng.shuffle(records)
    return records


def manual_records() -> list[RequestRecord]:
    records = []
    for index, (text, expected) in enumerate(MANUAL_CHALLENGE, start=1):
        records.append(
            RequestRecord(
                request_id=f"manual-{index:02d}",
                run_id=f"manual-run-{index:02d}",
                instruction_text=text,
                dataset_kind="hand_labeled_challenge",
                synthetic_flag=False,
                source_topic_id="independent",
                canonical_group_id=f"manual-{index:02d}",
                template_family_id=f"manual-{index:02d}",
                split="manual",
                dataset_version="manual-v1",
                expected_labels=expected,
            )
        )
    return records
