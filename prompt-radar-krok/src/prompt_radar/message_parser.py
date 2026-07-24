from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .security import redact
from .vector import normalize

ALLOWED_ROLES = {"system", "developer", "user", "assistant", "tool"}
ALL_AXES = ("system", "intent", "object", "automation_mode", "business_domain")
CONTEXT_RE = re.compile(r"(?is)<context\b[^>]*>(.*?)</context>")
USER_QUERY_RE = re.compile(r"(?is)<user_query\b[^>]*>(.*?)</user_query>")
TAG_RE = re.compile(r"(?s)<[^>]+>")


def _text_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
                continue
            if not isinstance(part, dict):
                raise ValueError("Unsupported message content part")
            text = part.get("text")
            if isinstance(text, str):
                parts.append(text)
                continue
            if isinstance(text, dict) and isinstance(text.get("value"), str):
                parts.append(text["value"])
                continue
            if part.get("type") not in {"image_url", "input_image"}:
                raise ValueError("Unsupported non-text message content part")
        return "\n".join(parts)
    raise ValueError("Message content must be a string or OpenAI content-parts list")


def _strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", value)).strip()


def _redact_section(text: str) -> tuple[str, int, bool, str]:
    if not text:
        return "", 0, False, "passed"
    return redact(text)


def _quarantine_result(
    request_id: str, payload: object, error: str
) -> dict[str, object]:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return {
        "request_id": request_id,
        "model": None,
        "stream": None,
        "message_count": 0,
        "current_user_goal": "",
        "task_wrapper": "",
        "retrieval_context": "",
        "conversation_history_user": "",
        "conversation_history_assistant": "",
        "system_context": "",
        "tool_messages": "",
        "system_context_chars": 0,
        "history_user_chars": 0,
        "history_assistant_chars": 0,
        "retrieval_context_chars": 0,
        "current_goal_chars": 0,
        "task_wrapper_chars": 0,
        "tool_message_chars": 0,
        "estimated_total_input_tokens": len(encoded.split()),
        "estimated_context_tokens": len(encoded.split()),
        "estimated_goal_tokens": 0,
        "context_to_goal_ratio": None,
        "prompt_injection_flag": False,
        "pii_redaction_count": 0,
        "redaction_status": "quarantine",
        "abstain_axes": list(ALL_AXES),
        "goal_source": "unavailable",
        "deduplicated_goal_repetitions": 0,
        "parse_error": error,
    }


def parse_openai_payload(
    payload: object, request_id: str | None = None
) -> dict[str, object]:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    resolved_request_id = request_id or (
        "message-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    )
    if not isinstance(payload, dict):
        return _quarantine_result(
            resolved_request_id, payload, "payload must be a JSON object"
        )
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        return _quarantine_result(
            resolved_request_id, payload, "messages must be a non-empty list"
        )

    parsed_messages: list[tuple[str, str]] = []
    try:
        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(f"messages[{index}] must be an object")
            role = message.get("role")
            if role not in ALLOWED_ROLES:
                raise ValueError(f"messages[{index}] has unsupported role")
            parsed_messages.append((str(role), _text_content(message.get("content", ""))))
    except ValueError as exc:
        return _quarantine_result(resolved_request_id, payload, str(exc))

    user_indexes = [
        index for index, (role, _) in enumerate(parsed_messages) if role == "user"
    ]
    if not user_indexes:
        return _quarantine_result(
            resolved_request_id, payload, "payload has no user message"
        )
    current_index = user_indexes[-1]
    current_content = parsed_messages[current_index][1]

    retrieval_parts = CONTEXT_RE.findall(current_content)
    without_context = CONTEXT_RE.sub(" ", current_content)
    tagged_queries = [
        _strip_tags(match).strip()
        for match in USER_QUERY_RE.findall(without_context)
        if _strip_tags(match).strip()
    ]
    unique_queries = {normalize(query) for query in tagged_queries}
    if len(unique_queries) > 1:
        return _quarantine_result(
            resolved_request_id, payload, "multiple distinct user_query values"
        )
    if tagged_queries:
        raw_goal = tagged_queries[-1]
        goal_source = "user_query_tag"
        wrapper = USER_QUERY_RE.sub(" ", without_context)
        occurrences = len(
            re.findall(re.escape(raw_goal), current_content, flags=re.IGNORECASE)
        )
        wrapper = re.sub(
            re.escape(raw_goal), " ", wrapper, flags=re.IGNORECASE
        )
        deduplicated = max(0, occurrences - 1)
    else:
        raw_goal = _strip_tags(without_context)
        goal_source = "last_user_message"
        wrapper = ""
        deduplicated = 0
    raw_goal = re.sub(r"\s+", " ", raw_goal).strip()
    if not raw_goal:
        return _quarantine_result(
            resolved_request_id, payload, "current user goal is empty"
        )

    history_user_raw = "\n".join(
        content
        for index, (role, content) in enumerate(parsed_messages)
        if role == "user" and index < current_index
    )
    history_assistant_raw = "\n".join(
        content
        for index, (role, content) in enumerate(parsed_messages)
        if role == "assistant" and index < current_index
    )
    system_raw = "\n".join(
        content
        for index, (role, content) in enumerate(parsed_messages)
        if role in {"system", "developer"} and index <= current_index
    )
    tool_raw = "\n".join(
        content
        for index, (role, content) in enumerate(parsed_messages)
        if role == "tool" and index < current_index
    )
    retrieval_raw = "\n".join(retrieval_parts)
    wrapper_raw = _strip_tags(wrapper)

    sections = {
        "current_user_goal": raw_goal,
        "task_wrapper": wrapper_raw,
        "retrieval_context": retrieval_raw,
        "conversation_history_user": history_user_raw,
        "conversation_history_assistant": history_assistant_raw,
        "system_context": system_raw,
        "tool_messages": tool_raw,
    }
    cleaned: dict[str, str] = {}
    redaction_count = 0
    injection = False
    for name, text in sections.items():
        value, count, flagged, status = _redact_section(text)
        cleaned[name] = value
        redaction_count += count
        injection = injection or flagged

    goal_tokens = len(raw_goal.split())
    total_tokens = sum(len(content.split()) for _, content in parsed_messages)
    context_tokens = max(0, total_tokens - goal_tokens)
    status = "quarantine" if cleaned["current_user_goal"] == "[QUARANTINED]" else "passed"
    if status == "quarantine":
        abstain_axes = list(ALL_AXES)
    else:
        abstain_axes = []
    return {
        "request_id": resolved_request_id,
        "model": payload.get("model"),
        "stream": payload.get("stream"),
        "message_count": len(parsed_messages),
        **cleaned,
        "system_context_chars": len(system_raw),
        "history_user_chars": len(history_user_raw),
        "history_assistant_chars": len(history_assistant_raw),
        "retrieval_context_chars": len(retrieval_raw),
        "current_goal_chars": len(raw_goal),
        "task_wrapper_chars": len(wrapper_raw),
        "tool_message_chars": len(tool_raw),
        "estimated_total_input_tokens": total_tokens,
        "estimated_context_tokens": context_tokens,
        "estimated_goal_tokens": goal_tokens,
        "context_to_goal_ratio": round(context_tokens / goal_tokens, 4)
        if goal_tokens
        else None,
        "actual_input_tokens": (payload.get("usage") or {}).get("prompt_tokens")
        if isinstance(payload.get("usage"), dict)
        else None,
        "actual_output_tokens": (payload.get("usage") or {}).get("completion_tokens")
        if isinstance(payload.get("usage"), dict)
        else None,
        "tool_call_count": payload.get("tool_call_count"),
        "latency_ms": payload.get("latency_ms"),
        "finish_reason": payload.get("finish_reason"),
        "error": payload.get("error"),
        "prompt_injection_flag": injection,
        "pii_redaction_count": redaction_count,
        "redaction_status": status,
        "abstain_axes": abstain_axes,
        "goal_source": goal_source,
        "deduplicated_goal_repetitions": deduplicated,
        "parse_error": None,
    }


def persisted_message_record(parsed: dict[str, object]) -> dict[str, object]:
    """Return the bounded, redacted projection allowed in default artifacts."""
    allowed = (
        "request_id",
        "model",
        "stream",
        "message_count",
        "current_user_goal",
        "system_context_chars",
        "history_user_chars",
        "history_assistant_chars",
        "retrieval_context_chars",
        "current_goal_chars",
        "task_wrapper_chars",
        "tool_message_chars",
        "estimated_total_input_tokens",
        "estimated_context_tokens",
        "estimated_goal_tokens",
        "context_to_goal_ratio",
        "actual_input_tokens",
        "actual_output_tokens",
        "tool_call_count",
        "latency_ms",
        "finish_reason",
        "error",
        "prompt_injection_flag",
        "pii_redaction_count",
        "redaction_status",
        "abstain_axes",
        "goal_source",
        "deduplicated_goal_repetitions",
        "parse_error",
    )
    return {key: parsed.get(key) for key in allowed}
