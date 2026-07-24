# Журнал решений

Этот файл — единственная актуальная точка правды по архитектуре. Каждый чат
читает его перед работой и обновляет только при принятии нового решения.

## Статус

- Этап: Gate-1 offline batch vertical slice реализован и проверен
- Gate 1: **PASS** для одного hackathon vertical slice; это не production gate
- Архитектура: Evidence-First Opportunity Radar с run-level unit economics
  сохранена после точечных исправлений red-team
- Главная демонстрационная история: sealed synthetic challenge
  «Email → Project ticket», паспорт доказательств и экран value/cost; это не
  заявление об открытии неизвестного КРОК сценария
- Стек: CPU-first локальный Python pipeline, multilingual embeddings,
  DuckDB/Parquet и Streamlit; LLM не входит в критический путь
- Ограничение вердикта: Gate не подтверждает ROI КРОК, production readiness
  или causal superiority agent platform над web chat

## Статус реализации P0/P1

Дата проверки: 2026-07-24.

- Ветка: `codex/p0-vertical-slice`; изменений в `main` не выполнялось.
- Реализован один offline CPU batch flow от исходного `A3:A33` XLSX до
  DuckDB/Parquet, evaluation report, статического HTML и Streamlit dashboard.
- `A32` и шесть независимо сформулированных производных находятся только в
  sealed test; dev/catalog/tuning их не содержат. Exact/near-duplicate leakage
  report: 0.
- Sealed residual passport имеет статус `emerging`, support 5 независимых
  canonical groups и mean/core aligned Jaccard 0.80 на 10 perturbation runs.
- Expected labels зафиксированы отдельным source-row/manual rubric и не
  вычисляются classifier; permutation test снижает score. На последнем clean
  run micro-F1: overall synthetic dev/test 0.7241, sealed synthetic 0.9512 при
  coverage 1.0, manual 0.9783 при coverage 0.875. Низкий общий synthetic score
  не скрывается; Gate-классификация относится к sealed challenge, а перенос на
  реальные логи не заявляется.
- Security fixture: email, телефон и seeded secret удалены до persistence;
  long-input injection обнаружена; persisted-artifact scan не нашёл canary;
  конфигурация не изменилась.
- 100k start/middle/end/injection suite прошёл на локальном CPU: p95 0.2115 s,
  peak traced sketch memory 11.41 MB. Метрики привязаны к hardware profile в
  `long_input.json` и не являются универсальным benchmark.
- Economics model check сохраняет success/partial/failed/cancelled в
  denominator, считает четыре distinct business tasks, даёт нулевую ошибку
  child-cost reconciliation и ограничивает действие уровнем `VALIDATE` на E0.
- Семь unit/integration tests проходят. Два неизменных запуска дали одинаковый
  fingerprint:
  `f6cea85dd68b558096a80751696b4940f7188f00df84242d823fb43f6adcc3da`.
- P2/P3, product comparison, causal estimates, GPU, external/local LLM,
  real-time и MLOps не начинались.

## Принятые решения

1. Выбрана одна продуктовая концепция: **Evidence-First Opportunity Radar**.
   Система разделяет известные, новые и неопределённые сценарии и показывает
   новый use case только после evidence gate.
2. Главная вау-фича: **«Паспорт нового сценария»** с support, cohesion,
   distinctness, stability, medoid/boundary-примерами, доступной динамикой и
   прозрачной action card.
3. Аналитическая модель многомерная:
   `system × intent × object × automation_mode × business_domain × use_case`.
   Классификация multi-label и поддерживает `abstain`.
4. Поиск нового выполняется только в residual pool после сопоставления с
   известными use cases. Кластер становится `emerging` только при достаточной
   поддержке, отличии от известных сценариев и устойчивом ядре.
5. Default demo работает offline и CPU-only. H100 может только ускорять batch
   embeddings или опциональное локальное именование; внешние API не являются
   зависимостью.
6. LLM не классифицирует каждый запрос. Именование кластеров по умолчанию
   extractive; локальная LLM допустима как заменяемый модуль и не влияет на
   membership.
7. Excel с 31 темой считается источником сценариев для генератора, а не
   реальным датасетом КРОК. Любые созданные события, timestamps, ответы и
   ошибки помечаются `synthetic_flag=true`.
8. Динамика показывается только при наличии timestamp. При нулевом предыдущем
   объёме выводится `NEW`, а при недостатке данных - `N/A/insufficient data`.
9. «Сломанные запросы» разделены на `confirmed failure`, `probable failure` и
   `quality risk`. По одному тексту запроса разрешён только `quality risk`;
   failure rate без telemetry не считается.
10. Требование 100k трактуется как нагрузочный профиль. Длинный запрос
    обрабатывается через structure-aware chunking и semantic sketch не более
    чем из 24 репрезентативных чанков с `coverage_warning`.
11. Главная demo-история: на явно синтетическом sealed test система проверяет
    use case «создание тикетов Project из входящих писем». Тема уже дана в
    `Лист1!A32`; она исключается из dev/catalog/tuning, а результат доказывает
    работу pipeline на challenge, но не открытие в реальных логах КРОК.
12. Полное обоснование и план зафиксированы в `docs/STRATEGY.md`.
13. Единица business volume, success и economics для agent platform -
    законченный `agent_run`, а не запрос, токен, LLM-вызов или tool call.
14. Все внутренние события связываются по `run_id`. Gross value учитывается не
    более одного раза на run; child costs суммируются в cost ledger этого run.
15. Экономическая модель включает `gross_value`, marginal и fully-loaded
    `agent_cost`, `net_value`, `ROI`, `value_cost_ratio`, raw и realized
    `net_saved_minutes`. Неуспешный run может иметь отрицательную ценность.
16. User active time, human review и rework вычитаются из saved time и входят в
    human-touch cost. FTE показывается только как capacity equivalent.
17. Expert baseline отделён от causal effect уровнями `E0-E3`. Для `E0/E1`
    обязательны low/base/high assumptions; 95% CI используется после
    paired/control измерения.
18. Web chat и agent platform сравниваются в primary analysis только по
    pre-outcome matched started/assigned jobs одного use case и сопоставимой
    сложности. Completion и quality - outcomes; per-completed-job является
    вторичной метрикой. Числа пользователей и токенов остаются контекстом.
19. Главный экономический экран - «ценность против стоимости»: cost per
    successful run, realized net value, evidence level и sensitivity.
    Рекомендация `SCALE` требует положительного conservative net value.
20. Synthetic generator должен создавать согласованные runs, LLM/tool calls,
    errors/retries, model/tool/infra costs, review/rework, baseline ranges и
    `synthetic_flag=true`.
21. Путь валидации: instrumentation -> time study -> paired crossover tasks ->
    контрольный или stepped-wedge pilot. Expert estimate нельзя переименовать в
    доказанный ROI без этого перехода.
22. Split назначается по `canonical_group_id/source_topic_id/template_family_id`
    до augmentation. Near-duplicates между dev/test запрещены; test открывается
    после freeze taxonomy, model, prompts, thresholds и generator version.
23. Synthetic evaluation не может самостоятельно пройти Gate: отдельно нужен
    независимо сформулированный hand-labeled challenge set. Synthetic economics
    проверяет формулы и reconciliation, а не бизнес-эффект.
24. Stability считается минимум на 10 perturbation runs с sampling по
    canonical groups и alignment кластеров до Jaccard. Вместе публикуются
    support, coverage, unresolved rate и known-only false discovery.
25. Quoting входного текста не считается защитой от prompt injection.
    Redaction выполняется до embeddings/cache/dashboard; optional naming-LLM
    не имеет tools, network и raw-store access; сомнительные записи
    quarantined.
26. 100k smoke/stress path перенесён в P0 как буквальное требование кейса.
    Needle start/middle/end и injection обязательны; при слабом coverage
    система abstains, а не выдаёт уверенную классификацию.
27. `TRAIN_USERS` нельзя рекомендовать только по low confidence: нужна
    наблюдаемая связь формулировки с outcome. `SCALE/AUTOMATE` запрещён на `E0`.
28. MVP economics считается только по явным или однозначно валидированным
    `run_id`; неоднозначная reconstruction приводит к `N/A/quarantine`.
29. Hackathon scope ограничен одним offline CPU batch flow, одним dashboard,
    одним evidence passport, одним reconciled synthetic economics card, одним
    100k smoke test и одним evaluation report. GPU, external API, local LLM,
    causal pilot, real-time и MLOps не блокируют demo.

## Отклонённые варианты

1. **Taxonomy Control Tower как самостоятельный продукт** - устойчив и понятен,
   но почти не обнаруживает неизвестные use cases.
2. **Pure Semantic Discovery / BERTopic-first** - хорошо выглядит на карте, но
   нестабилен на малом наборе и может склеивать бизнес-разные намерения.
3. **LLM Analyst Council** - слишком зависим от API/GPU, latency и
   недетерминизма; создаёт убедительные тексты без гарантии evidence.
4. **Workflow Graph Miner** - интересен для следующего этапа, но extraction,
   graph mining и визуализация слишком рискованны для сроков хакатона.
5. **Перегруженный комбайн из графа, multi-agent анализа, forecasting и чата с
   дашбордом** - отклонён как не помогающий доказать центральное качество
   группировки и novelty detection.
6. **Запрос, токен или внутренний LLM-вызов как единица пользы** - создаёт
   двойной счёт и вознаграждает дорогие циклы.
7. **Прямое сравнение 1300 web-chat и 150 agent users** - продукты решают
   задачи разной сложности; primary comparison допустим только по
   pre-outcome matched started/assigned jobs.
8. **Expert minutes как доказанная экономия** - остаются proxy assumption
   `E0`, а не causal effect.
9. **Одна точка денежного ROI без диапазона и cost mode** - скрывает baseline,
   quality, labor rate и распределение командных затрат.
10. **Расчёт только по успешным runs** - отклонён из-за survivorship bias;
    failed/partial runs входят в denominator и cost.

## Открытые вопросы организаторам

1. Что означает «средний размер запроса 100k токенов»?
2. Как именно ограничено использование H100?
3. Будут ли реальные `run_id`, tool/LLM events, outcomes, ответы и ошибки?
4. Разрешено ли использовать внешние API во время демонстрации?
5. Доступны ли versioned token prices, infrastructure spend и годовой бюджет
   команды для marginal/fully-loaded cost?
6. Как бизнес определяет `success`, `partial success` и acceptable quality для
   ключевых use cases?
7. Есть ли измерения human baseline, review/rework или возможность провести
   paired/control pilot?

## Следующий обязательный gate

Следующий этап - P0 implementation gate. Реализация ещё не начиналась.

P0 пройден только если:

1. classification/abstain, known matching, grounded extractive summary и один
   dashboard проходят end-to-end на зафиксированном contract;
2. split назначен до augmentation, A32 отсутствует в dev/catalog/tuning, а
   leakage report не находит cross-split duplicates;
3. synthetic и independently hand-labeled метрики опубликованы раздельно
   вместе с coverage;
4. reconstruction даёт одну business task и не более одной gross value на
   валидированный `run_id`; child costs сходятся, failures остаются в
   denominator;
5. adversarial fixture не раскрывает seeded PII/secrets и не меняет pipeline
   под инструкцией из входного текста;
6. CPU-only 100k smoke с needle start/middle/end не падает и либо сохраняет
   intent, либо честно abstains с `coverage_warning`;
7. dashboard различает `SYNTHETIC`, `E0`, `E1`, `E2/E3` и `N/A`;
8. default demo полностью проходит без сети, H100 и naming-LLM.

Полная окончательная спецификация Gate 1 и вопросы жюри находятся в
`docs/RED_TEAM.md`. Расширять scope новыми крупными подсистемами до прохождения
P0 нельзя.
