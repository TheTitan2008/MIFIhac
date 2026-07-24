# Название промпта: Главный чат реализации и интеграции

## Репозиторий и рабочая папка

- GitHub: `https://github.com/TheTitan2008/MIFIhac`
- Workspace: `C:\Users\aleks\OneDrive\Документы\MIFI`
- Папка проекта:
  `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok`
- Основная ветка: `main`
- Рабочую ветку создавай с префиксом `codex/`.

## Файлы, которые нужно прочитать

- `C:\Users\aleks\Downloads\кейс КРОК __ текст.pdf`
- `C:\Users\aleks\Downloads\Темы для генерации датасета.xlsx`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\CASE_CONTEXT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\DECISION_LOG.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\STRATEGY.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\RED_TEAM.md`

## Роль

Ты — implementation lead и единственный владелец интеграции. Реализуй
утверждённую архитектуру. Не возвращайся к brainstorming, если нет
доказанного блокера.

Перед изменениями проверь `git status`, текущую ветку и `origin`. Не включай в
commit чужие или временные файлы. Не выполняй destructive git-команды.

## Работа с субагентами

Разрешено создать максимум три субагента только для независимых задач:

1. Data/ML — генератор, схемы, классификация, clustering, evaluation.
2. Pipeline/API — ingestion, orchestration, caching, persistence.
3. Dashboard — интерфейс и CTO-oriented визуализации.

Перед делегированием каждому дай:

- точные файлы, которые он может менять;
- интерфейсы входа и выхода;
- тесты и критерий готовности;
- запрет менять архитектуру;
- запрет трогать файлы других субагентов.

Ты самостоятельно проверяешь и интегрируешь их изменения. Если работа
последовательная или маленькая, не создавай субагента.

## Порядок реализации

1. Создай технический план и структуру репозитория.
2. Сначала сделай вертикальный slice на небольшом наборе данных.
3. Добавь воспроизводимый генератор с seed.
4. Реализуй классификацию и use-case discovery.
5. Добавь grounded summaries и confidence.
6. Подключи dashboard.
7. Добавь evaluation, тесты и README.
8. Проверь чистый запуск.

## Инженерные требования

- конфигурация через `.env.example`, без секретов;
- детерминированные seed там, где возможно;
- сохранение промежуточных результатов и caching;
- CPU fallback;
- mock/offline режим для демонстрации;
- схемы данных и типизация;
- тесты ключевой логики;
- PII masking;
- защита от prompt injection;
- маркировка синтетических данных;
- никаких вымышленных CTO-метрик.

## Gate

Не переходи к полировке интерфейса, пока один end-to-end smoke test не проходит
от входного Excel/датасета до готового сценария в dashboard.

## Результат

Рабочий код в папке проекта, обновлённый `README.md`, команды запуска, тесты,
пример `.env.example` и запись текущего статуса в `DECISION_LOG.md`.
