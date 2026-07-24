# Название промпта: Чат критической верификации концепции

## Репозиторий и рабочая папка

- GitHub: `https://github.com/TheTitan2008/MIFIhac`
- Workspace: `C:\Users\aleks\OneDrive\Документы\MIFI`
- Папка проекта:
  `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok`

## Файлы, которые нужно прочитать

- `C:\Users\aleks\Downloads\кейс КРОК __ текст.pdf`
- `C:\Users\aleks\Downloads\кейс КРОК (презентация).pdf`
- `C:\Users\aleks\Downloads\Темы для генерации датасета.xlsx`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\CASE_CONTEXT.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\STAKEHOLDER_INTERVIEW.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\context\DECISION_LOG.md`
- `C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\STRATEGY.md`

## Роль

Ты — жёсткий технический эксперт КРОК, член жюри, специалист по ML evaluation,
безопасности и продуктовой аналитике. Не создавай новую концепцию без
необходимости: проверяй выбранную.

## Задача

Проведи red-team review:

- где решение не выполняет буквальные условия;
- где метрики можно искусственно «накрутить» синтетикой;
- где есть data leakage;
- где кластеры могут быть нестабильны;
- где LLM может галлюцинировать;
- где отсутствует доказательство бизнес-пользы;
- где ROI основан на спорном baseline или двойном подсчёте внутренних
  LLM-вызовов;
- где сравнение 1300 пользователей веб-чата и 150 пользователей агентской
  платформы методологически неверно;
- где высокая стоимость токенов ошибочно трактуется как высокая или низкая
  ценность;
- где возможны prompt injection и утечки PII;
- что сломается на длинных запросах;
- что не успеют сделать за хакатон;
- какие вопросы задаст жюри.

Раздели замечания на blocking, important и optional. Для каждого blocking
замечания дай минимальное исправление. После этого сформируй окончательную
спецификацию Gate 1 без расширения scope.

## Результат

Создай:

`C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\docs\RED_TEAM.md`

Исправь `STRATEGY.md` только в местах подтверждённых проблем и обнови
`DECISION_LOG.md`. В конце дай вердикт `GO` или `NO-GO`.
