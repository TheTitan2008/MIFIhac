# Название промпта: Независимый sealed v2 и однократный recovery gate

## Репозиторий и рабочая папка

- GitHub: `https://github.com/TheTitan2008/MIFIhac`
- Workspace: `C:\Users\aleks\OneDrive\Документы\MIFI`
- Ветка кандидата: `codex/p0-recovery-v2`

## Файлы, которые нужно прочитать

- `C:\Users\aleks\Downloads\кейс КРОК __ текст.pdf`
- `C:\Users\aleks\Downloads\Темы для генерации датасета.xlsx`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\QA_REPORT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\LABEL_GUIDE.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\RECOVERY_FREEZE.md`

## Роль и независимость

Ты — независимый evaluator. Не продолжай работу implementation lead.
Кандидат уже заморожен. Нельзя менять classifier, taxonomy, thresholds,
label guide, pipeline или tests после создания challenge.

Если возможно, попроси бизнес-эксперта или второго человека проверить labels.
Если это невозможно, честно укажи provenance:
`independent model-assisted adjudication, not business-expert gold`.

## Задача

1. Проверь, что текущий commit и hashes совпадают с `RECOVERY_FREEZE.md`.
2. До запуска модели создай versioned challenge минимум из 24 новых запросов:
   - несколько систем и бизнес-доменов;
   - one-shot, recurring и monitoring;
   - single-label и multi-label intents;
   - близкие `create/update/search/summarize`;
   - опечатки, разговорная речь и multi-intent;
   - несколько допустимых abstention cases;
   - без копирования development-шаблонов.
3. Разметь каждую строку по `LABEL_GUIDE.md` с:
   - expected labels;
   - evidence span;
   - rationale;
   - adjudicator/provenance;
   - ambiguity flag.
4. Сохрани challenge и SHA-256 до оценки.
5. Зафиксируй gates до запуска:
   - coverage `>= 0.80`;
   - macro-F1 ключевых осей `system/intent/object >= 0.80`;
   - отсутствующие классы не включаются в macro-F1;
   - ambiguous rows показываются отдельно;
   - никакого изменения thresholds после результата.
6. Один раз выполни `evaluate-external`.
7. Создай `docs/SEALED_V2_REPORT.md`:
   - candidate commit/hash;
   - challenge hash и provenance;
   - все метрики и coverage;
   - ошибки построчно после завершения оценки;
   - вердикт `GO` или `NO-GO`;
   - явное указание, что это не доказательство production readiness или ROI.
8. Проверь, что после freeze не изменились исходники кандидата.
9. Закоммить только challenge, provenance и отчёт. Не исправляй модель и не
   выполняй merge.

## Правило остановки

Если gate не пройден, результат остаётся `NO-GO`. Второй sealed v2 создавать
нельзя. Следующий цикл должен называться v3 и начинаться с нового candidate
freeze.

