# Название промпта: Финальный чат аудита сдачи

## Репозиторий и рабочая папка

- GitHub: `https://github.com/TheTitan2008/MIFIhac`
- Workspace: `C:\Users\aleks\OneDrive\Документы\MIFI`
- Папка проекта:
  `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok`
- Основная ветка: `main`

## Файлы, которые нужно прочитать

- `C:\Users\aleks\Downloads\кейс КРОК __ текст.pdf`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\CASE_CONTEXT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\STAKEHOLDER_INTERVIEW.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\DECISION_LOG.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\QA_REPORT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\PITCH.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\DEMO_SCRIPT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\README.md`

## Роль

Ты — релиз-менеджер. Не добавляй функциональность. Твоя задача — убедиться,
что всё обещанное существует и сдача не развалится из-за упаковки.

## Проверка

- репозиторий чистый и не содержит секретов;
- README запускается буквально по шагам;
- датасет или генератор присутствует;
- отчёт/дашборд открывается;
- тесты проходят;
- demo fallback готов;
- ссылки и пути корректны;
- лицензии и источники моделей указаны;
- синтетические данные помечены;
- обещания в питче совпадают с прототипом.
- экономическая модель не скрывает assumptions и не считает внутренние
  LLM-вызовы отдельными бизнес-результатами.

## Результат

Создай `docs/RELEASE_CHECKLIST.md`, исправь только упаковочные дефекты и выдай
однозначный статус `READY` или список оставшихся blockers.
