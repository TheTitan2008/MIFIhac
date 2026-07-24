# Название промпта: Recovery — заморозка нового кандидата без tuning на sealed v1

## Репозиторий и рабочая папка

- GitHub: `https://github.com/TheTitan2008/MIFIhac`
- Workspace: `C:\Users\aleks\OneDrive\Документы\MIFI`
- Исходная ветка: `codex/p0-vertical-slice`
- Создай рабочую ветку: `codex/p0-recovery-v2`

## Файлы, которые нужно прочитать

- `C:\Users\aleks\Downloads\кейс КРОК __ текст.pdf`
- `C:\Users\aleks\Downloads\Темы для генерации датасета.xlsx`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\STRATEGY.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\RED_TEAM.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\P0_PLAN.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\QA_REPORT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\DECISION_LOG.md`

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
2. Улучши общую multi-label логику только на разрешённых development-источниках.
3. Добавь внешний интерфейс:

```text
python -m prompt_radar evaluate-external --input <opaque.jsonl> --output <dir>
```

   Он должен принимать challenge после freeze, считать заранее определённые
   метрики и не менять модель, taxonomy, thresholds или config.
4. Протестируй интерфейс на dummy development fixture, не имитирующем будущий
   sealed v2.
5. Сохрани прежний sealed v1 failure как исторический diagnostic.
6. Запусти unit/regression tests, security scan и обычный offline smoke.
7. Создай `docs/RECOVERY_FREEZE.md`:
   - commit SHA кандидата;
   - source/config/taxonomy hashes;
   - фиксированные gates;
   - список использованных development-источников;
   - декларацию, что sealed v2 ещё не существовал.
8. Закоммить и push ветку `codex/p0-recovery-v2`.
9. Остановись. Не запускай финальную оценку и не создавай PR/merge.

## Критерий готовности

Есть неизменяемый candidate commit и внешний evaluation interface. После
freeze никакие изменения классификатора, taxonomy, thresholds и label guide
до получения результата sealed v2 недопустимы.

