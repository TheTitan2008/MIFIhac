# Уточнения из Telegram-чата экспертов

Источники:

- `C:\Users\aleks\Downloads\Telegram Desktop\ChatExport_2026-07-24\messages.html`
- `C:\Users\aleks\Downloads\Telegram Desktop\Структура запроса.txt`

Дата сообщений: 2026-07-24.

## Подтверждённый входной контракт

Татьяна Белякова приложила файл `Структура запроса.txt` и пояснила:

> «вот так хранятся запросы пользователей в БД»

Файл является валидным OpenAI-compatible request payload:

```json
{
  "stream": true,
  "model": "DeepSeek-V4-Flash",
  "stream_options": {"include_usage": true},
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```

Пример имеет четыре сообщения:

| role | chars | words | смысл |
|---|---:|---:|---|
| system | 45 | 7 | user context |
| user | 63 | 9 | предыдущая пользовательская цель |
| assistant | 4 236 | 573 | предыдущий ответ |
| user | 16 479 | 2 241 | task wrapper, RAG context и текущий query |

Всего: 20 823 символа и 2 830 whitespace words. Участники оценивали пример
примерно в 7k токенов.

## 100k — буквальное требование

На вопрос, действительно ли речь идёт об одном запросе, Татьяна ответила:

> «Пример специально маленький прислала. Для понимания структуры. Запросы на
> агента давайте 100к».

Следовательно:

- 100k относится к одному сохранённому agent request payload;
- это не просто максимальная память переписки;
- основную длину могут создавать история, предыдущие ответы, инструкции и RAG
  документы, а не последняя человеческая фраза;
- P0 обязан иметь message-aware 100k path, а не только обработку плоской строки.

## Главный риск текущей классификации

Нельзя объединять все `messages[*].content` в один текст и классифицировать его.
Внутренний RAG-документ может быть на десятки тысяч токенов и полностью
перетянуть тему на себя.

Нужно разделять:

1. `current_user_goal` — фактический последний вопрос пользователя;
2. `task_wrapper` — системные инструкции внутри последнего сообщения;
3. `retrieval_context` — содержимое `<context>/<source>`;
4. `conversation_history_user`;
5. `conversation_history_assistant`;
6. `system_context`;
7. `tool_messages`, если они присутствуют.

Классификация use case должна в первую очередь опираться на
`current_user_goal`, а контекст использовать только для уточнения системы,
объекта и сложности.

## Особенности примера

- Последний пользовательский message содержит `<user_query>`, RAG source и
  затем повторяет query после закрывающих тегов.
- Нужна дедупликация повторённой цели.
- В RAG source присутствуют персональные данные и контакты; redaction должна
  выполняться до persistence, embeddings и dashboard.
- Предыдущий assistant response не является новой пользовательской задачей.
- Payload является тестовым, а не реальным production-запросом. Татьяна прямо
  ответила: «Тестовый».
- Структура при этом дана как репрезентативная для хранения в БД.

## Дополнительные требования экспертов

### Оценка эффективности

Компания уже пробовала оценивать агентский продукт по использованию
инструментов, но считает этот подход недостаточным.

Прямое месячное сравнение:

```text
agent platform ↔ web chat
```

эксперты считают некорректным. Допустимы:

```text
agent ↔ agent
chat ↔ chat
```

Сравнение agent и chat возможно только как специально спроектированный
matched/paired experiment на одинаковых бизнес-задачах, а не как dashboard
месячных пользователей или токенов.

### Формат продукта

На вопрос «MVP-dashboard или модель?» Татьяна ответила:

> «Вам нужно вытащить данные, чтобы понять по ним эффективность использования
> агентов. Дашборд опционально для презы и видимости, но ценность в сервисе».

Следовательно:

- core value — корректный extraction/analytics service;
- dashboard является интерфейсом демонстрации, а не главным продуктом;
- технический pipeline важнее визуальной полировки;
- сервис должен принимать OpenAI-compatible payload или выгрузку таких
  payload из БД.

### Проверка данных

Татьяна сообщила:

> «На вашем потестим».

Это означает, что организаторы ожидают воспроизводимый собственный датасет и
могут запускать решение на нём. Нельзя рассчитывать на скрытый production
dataset при защите.

### Совместимость

На вопрос о модельном интерфейсе был дан ответ:

> «Openai compatible».

Даже если P0 работает offline без LLM, входной adapter и будущий model adapter
должны использовать OpenAI-compatible schema.

## Обязательные поля после разбора payload

```text
request_id
model
stream
message_count
current_user_goal
system_context_chars
history_user_chars
history_assistant_chars
retrieval_context_chars
current_goal_chars
estimated_total_input_tokens
estimated_context_tokens
estimated_goal_tokens
context_to_goal_ratio
prompt_injection_flag
redaction_status
```

Если доступен response/gateway telemetry:

```text
actual_input_tokens
actual_output_tokens
tool_call_count
latency_ms
finish_reason
error
```

## Новая P0-проверка

Минимальный fixture должен доказать:

1. OpenAI-compatible JSON успешно разбирается.
2. Текущая пользовательская цель извлекается отдельно от RAG context.
3. Повтор query удаляется.
4. Предыдущий assistant response не классифицируется как пользовательская цель.
5. PII из source context не попадает в persisted artifacts.
6. При 100k payload цель корректно извлекается в начале, середине и конце.
7. Контекст с другой тематикой не меняет основной intent цели.
8. Неизвестная структура приводит к abstention/quarantine, а не к уверенной
   классификации.

