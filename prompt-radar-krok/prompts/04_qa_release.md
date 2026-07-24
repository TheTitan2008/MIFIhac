# Название промпта: Чат QA, воспроизводимости и безопасности

## Репозиторий и рабочая папка

- GitHub: `https://github.com/TheTitan2008/MIFIhac`
- Workspace: `C:\Users\aleks\OneDrive\Документы\MIFI`
- Папка проекта:
  `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok`

## Файлы, которые нужно прочитать

- `C:\Users\aleks\Downloads\кейс КРОК __ текст.pdf`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\CASE_CONTEXT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\STAKEHOLDER_INTERVIEW.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\DECISION_LOG.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\STRATEGY.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\RED_TEAM.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\README.md`

## Роль

Ты — независимый senior reviewer. Сначала диагностируй и документируй, затем
исправляй только подтверждённые дефекты. Не добавляй новые продуктовые фичи.

## Проверки

- чистая установка по README;
- полный smoke test;
- тесты и ошибки;
- детерминированность генератора;
- отсутствие утечек между train/test;
- честность метрик;
- отсутствие двойного подсчёта внутренних LLM-вызовов;
- корректность формул saved time, cost, net value и ROI;
- отображение неопределённости экспертных baseline;
- качество multi-label классификации;
- устойчивость группировки;
- groundedness названий и саммари;
- обработка дублей, пустых строк, длинных и multi-intent запросов;
- PII и prompt injection;
- отсутствие секретов;
- CPU/offline demo fallback;
- dashboard без пустых и вводящих в заблуждение состояний.

## Результат

Создай `docs/QA_REPORT.md` с таблицей:

```text
severity | evidence | impact | fix | verification
```

Исправь blocking и high дефекты, перезапусти проверки и выдай финальный
вердикт готовности к демо. Не переписывай работающие модули ради стиля.
