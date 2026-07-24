from __future__ import annotations

SEED = 20260724
DATASET_VERSION = "synthetic-v1"
SCHEMA_VERSION = "request-event-v2-openai-messages"
TAXONOMY_VERSION = "taxonomy-v2-label-guide"
ALGORITHM_VERSION = "offline-message-aware-v2"
SEALED_SOURCE_TOPIC = "A32"
ABSTAIN_THRESHOLD = 0.58
KNOWN_MATCH_THRESHOLD = 0.48
RESIDUAL_SIMILARITY_THRESHOLD = 0.24
NEAR_DUPLICATE_THRESHOLD = 0.92

TAXONOMY = {
    "system": [
        "Email", "CRM", "Jira", "ISUP", "Project", "Calendar",
        "Confluence", "Excel", "CoolFeedback", "OpenWeb", "Other",
    ],
    "intent": [
        "search", "summarize", "create", "update", "reply", "export",
        "monitor", "notify", "schedule", "explain",
    ],
    "object": [
        "email", "client", "deal", "tender", "task", "project", "meeting",
        "room", "document", "employee_note", "report",
    ],
    "automation_mode": ["one_shot", "recurring", "monitoring", "notification"],
    "business_domain": ["sales", "projects", "HR", "knowledge", "productivity"],
}

SYSTEM_KEYWORDS = {
    "Email": ("почт", "письм", "email", "переписк"),
    "CRM": ("crm", "клиент", "сделк", "тендер", "продаж"),
    "Jira": ("jira",),
    "ISUP": ("исуп",),
    "Project": ("project", "доск"),
    "Calendar": ("календар", "встреч", "переговорн", "слот"),
    "Confluence": ("confluence",),
    "Excel": ("excel", "таблиц", "xlsx"),
    "CoolFeedback": ("coolfeedback",),
    "OpenWeb": ("открыт", "блог", "поставщик"),
}

INTENT_KEYWORDS = {
    "search": (
        "найт", "найд", "покаж", "поиск", "узнать", "собрать информацию", "контакт",
    ),
    "summarize": ("сводк", "саммар", "итог", "структурир", "обзор", "собер", "результат"),
    "create": ("созда", "добав", "завест", "завед", "запис", "перенес", "преврат", "сформир"),
    "update": ("редакт", "актуализ", "измен", "подтверд", "статус"),
    "reply": ("ответ", "написать ему", "отзыв"),
    "export": ("экспорт", "выгруз", "в excel", "отчет в excel"),
    "monitor": ("монитор", "отслеж", "контрол", "следи"),
    "notify": ("уведом", "напомин", "напомн", "подсвеч"),
    "schedule": ("заплан", "свободн", "создать встреч", "переговорн"),
    "explain": ("объясн", "почему", "ошибк"),
}

OBJECT_KEYWORDS = {
    "email": ("почт", "письм", "переписк"),
    "client": ("клиент", "компани", "контакт"),
    "deal": ("сделк", "продаж"),
    "tender": ("тендер",),
    "task": ("задач", "тикет"),
    "project": ("проект", "исуп"),
    "meeting": ("встреч", "календар", "обсужден"),
    "room": ("переговорн",),
    "document": ("документ", "confluence", "блог", "текстов"),
    "employee_note": ("сотрудник", "наблюден", "мониторинг", "отзыв"),
    "report": ("отчет", "аналитик", "сводк", "excel"),
}

KNOWN_USE_CASES = [
    {
        "scenario_id": "known-email-digest",
        "name": "Сводка входящей почты",
        "systems": ["Email"],
        "intents": ["summarize"],
        "prototype": "подготовить краткую структурированную сводку входящих писем",
    },
    {
        "scenario_id": "known-client-research",
        "name": "Поиск информации о клиенте",
        "systems": ["CRM", "OpenWeb"],
        "intents": ["search", "summarize"],
        "prototype": "собрать информацию о компании клиенте из CRM и открытых источников",
    },
    {
        "scenario_id": "known-mail-monitor",
        "name": "Мониторинг писем без ответа",
        "systems": ["Email"],
        "intents": ["monitor", "notify"],
        "prototype": "регулярно отслеживать письма без ответа и уведомлять пользователя",
    },
    {
        "scenario_id": "known-sales-report",
        "name": "Отчёт по продажам и тендерам",
        "systems": ["CRM", "Excel"],
        "intents": ["export", "summarize", "notify"],
        "prototype": "сформировать отчет по выигранным тендерам и продажам в Excel",
    },
    {
        "scenario_id": "known-task-management",
        "name": "Управление задачами",
        "systems": ["Jira", "ISUP"],
        "intents": ["search", "create", "update"],
        "prototype": "найти создать или обновить задачу в Jira или ИСУП",
    },
    {
        "scenario_id": "known-knowledge-search",
        "name": "Поиск корпоративных знаний",
        "systems": ["Confluence", "OpenWeb"],
        "intents": ["search"],
        "prototype": "найти документ процесс или новость в Confluence и корпоративном блоге",
    },
    {
        "scenario_id": "known-calendar",
        "name": "Планирование встреч",
        "systems": ["Calendar"],
        "intents": ["schedule", "search"],
        "prototype": "найти общий свободный слот переговорную и запланировать встречу",
    },
    {
        "scenario_id": "known-notes",
        "name": "Заметки и обратная связь",
        "systems": ["CoolFeedback"],
        "intents": ["create", "summarize", "reply"],
        "prototype": "зафиксировать итоги наблюдения или обратную связь сотруднику",
    },
]
