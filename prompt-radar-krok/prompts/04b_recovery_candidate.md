# Название промпта: Recovery — заморозка нового кандидата без tuning на sealed v1

## Репозиторий и рабочая папка

- GitHub: `https://github.com/TheTitan2008/MIFIhac`
- Workspace: `C:\Users\aleks\OneDrive\Документы\MIFI`
- Исходная ветка: `codex/p0-vertical-slice`
- Создай рабочую ветку: `codex/p0-recovery-v2`

## Файлы, которые нужно прочитать

- `C:\Users\aleks\Downloads\кейс КРОК __ текст.pdf`
- `C:\Users\aleks\Downloads\Темы для генерации датасета.xlsx`
- `C:\Users\aleks\Downloads\Telegram Desktop\Структура запроса.txt`
- `C:\Users\aleks\Downloads\Telegram Desktop\ChatExport_2026-07-24\messages.html`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\STRATEGY.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\RED_TEAM.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\P0_PLAN.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\QA_REPORT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\DECISION_LOG.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\TELEGRAM_FINDINGS.md`

## Роль

Ты — implementation lead recovery-этапа. QA обнаружил честный NO-GO.
Исправляй метод, но не подгоняй его под раскрытый sealed v1.

## Неприкосновенные ограничения

- Sealed v1 навсегда считается раскрытым диагностическим набором.
- Не изменяй его тексты, labels, rubric или ожидаемые результаты.
- Не меняй gate thresholds ради прохождения.
- Не используй sealed v1 score для выбора правил, весов или confidence.
- Не изменяй `QA_REPORT.md`.
- Не создавай новый sealed v2: его после freeze создаст независимый QA.
- Не добавляй LLM, сеть, GPU или P2/P3.

## Допустимые источники разработки

- исходный текст кейса и общая предметная таксономия;
- dev/train данные;
- открытый manual challenge как development diagnostic, но не как финальный
  независимый gold;
- общие инварианты multi-label классификации;
- regression tests, не содержащие будущий sealed v2.

## Задача

1. Создай явный `docs/LABEL_GUIDE.md`:
   - определения всех осей и labels;
   - правила multi-label;
   - правило `create` против `update`;
   - неоднозначные случаи и abstention;
   - построчная evidence requirement.
2. Реализуй OpenAI-compatible ingestion adapter:
   - разбор `messages` по ролям;
   - выделение current user goal;
   - отделение system/history/assistant/RAG context;
   - извлечение `<user_query>` и дедупликация повторённого query;
   - redaction до persistence;
   - явный abstention для неизвестного payload;
   - метрики context/goal token ratio.
3. Добавь regression fixture на структуре из
   `Структура запроса.txt` и 100k message-aware cases. Тема длинного RAG
   context не должна менять intent короткой пользовательской цели.
4. Улучши общую multi-label логику только на разрешённых development-источниках.
5. Добавь внешний интерфейс:

```text
python -m prompt_radar evaluate-external --input <opaque.jsonl> --output <dir>
```

   Он должен принимать challenge после freeze, считать заранее определённые
   метрики и не менять модель, taxonomy, thresholds или config.
6. Протестируй интерфейс на dummy development fixture, не имитирующем будущий
   sealed v2.
7. Сохрани прежний sealed v1 failure как исторический diagnostic.
8. Запусти unit/regression tests, security scan и обычный offline smoke.
9. Создай `docs/RECOVERY_FREEZE.md`:
   - commit SHA кандидата;
   - source/config/taxonomy hashes;
   - фиксированные gates;
   - список использованных development-источников;
   - декларацию, что sealed v2 ещё не существовал.
10. Закоммить и push ветку `codex/p0-recovery-v2`.
11. Остановись. Не запускай финальную оценку и не создавай PR/merge.

## Критерий готовности

Есть неизменяемый candidate commit и внешний evaluation interface. После
freeze никакие изменения классификатора, taxonomy, thresholds и label guide
до получения результата sealed v2 недопустимы.
