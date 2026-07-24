from __future__ import annotations

import re

INJECTION_RE = re.compile(
    r"(ignore\s+(all\s+)?previous|reveal\s+(logs?|secrets?)|"
    r"раскрой\s+(логи|секрет)|игнорируй\s+(все\s+)?предыдущ)",
    re.IGNORECASE,
)
PATTERNS = [
    (re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-zА-Яа-я]{2,}\b"), "[EMAIL]"),
    (re.compile(r"(?<!\d)(?:\+7|8)[\s()-]*\d{3}[\s()-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}(?!\d)"), "[PHONE]"),
    (re.compile(r"\b(?:sk|api|token|secret)[-_][A-Za-z0-9_-]{8,}\b", re.IGNORECASE), "[SECRET]"),
    (re.compile(r"\b(?:договор|contract)[\s:#№-]*[A-Za-zА-Яа-я0-9/-]{4,}\b", re.IGNORECASE), "[IDENTIFIER]"),
    (re.compile(r"https?://(?:[\w-]+\.)*(?:corp|internal|local)(?:/[\w./?=&%-]*)?", re.IGNORECASE), "[INTERNAL_URL]"),
]


def redact(text: str) -> tuple[str, int, bool, str]:
    cleaned = text
    count = 0
    for pattern, replacement in PATTERNS:
        cleaned, replaced = pattern.subn(replacement, cleaned)
        count += replaced
    injection = bool(INJECTION_RE.search(cleaned))
    if injection:
        cleaned = INJECTION_RE.sub("[UNTRUSTED_INSTRUCTION]", cleaned)
    uncertain_person = re.search(
        r"\b(?:PERSON|ФИО)\s*:\s*[A-ZА-ЯЁ][A-Za-zА-Яа-яЁё-]+"
        r"(?:\s+[A-ZА-ЯЁ][A-Za-zА-Яа-яЁё-]+){1,2}",
        cleaned,
        re.IGNORECASE,
    )
    status = "quarantine" if uncertain_person else "passed"
    if status == "quarantine":
        cleaned = "[QUARANTINED]"
    return cleaned, count, injection, status
