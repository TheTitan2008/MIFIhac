# Журнал решений

Этот файл — единственная актуальная точка правды по архитектуре. Каждый чат
читает его перед работой и обновляет только при принятии нового решения.

## Статус

- Этап: стратегия обновлена по интервью, ожидается red-team
- Gate 1: **PASS WITH CONDITIONS**
- Архитектура: Evidence-First Opportunity Radar с run-level unit economics
  утверждена для red-team
- Главная демонстрационная история: рождение нового сценария
  «Email → Project ticket», паспорт доказательств и экран value/cost
- Стек: CPU-first локальный Python pipeline, multilingual embeddings,
  DuckDB/Parquet и Streamlit; LLM не входит в критический путь

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
11. Главная demo-история: на явно синтетическом потоке система обнаруживает
    ранее не заведённый use case «создание тикетов Project из входящих писем»,
    доказывает его устойчивость и предлагает исследовать автоматизацию.
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
18. Web chat и agent platform сравниваются только по matched completed jobs
    одного use case и quality threshold. Числа пользователей и токенов остаются
    контекстом масштаба.
19. Главный экономический экран - «ценность против стоимости»: cost per
    successful run, realized net value, evidence level и sensitivity.
    Рекомендация `SCALE` требует положительного conservative net value.
20. Synthetic generator должен создавать согласованные runs, LLM/tool calls,
    errors/retries, model/tool/infra costs, review/rework, baseline ranges и
    `synthetic_flag=true`.
21. Путь валидации: instrumentation -> time study -> paired crossover tasks ->
    контрольный или stepped-wedge pilot. Expert estimate нельзя переименовать в
    доказанный ROI без этого перехода.

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
   задачи разной сложности; сравнение допустимо только по matched jobs.
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

Провести red-team выбранной архитектуры до начала основной реализации.

Gate пройден только если:

1. reconstruction даёт одну business task и не более одной записи gross value
   на `run_id`, независимо от числа внутренних вызовов;
2. сумма child costs сверяется с run cost, а failure/partial runs остаются в
   denominator;
3. low/base/high и marginal/fully-loaded режимы меняют action card прозрачно и
   не содержат скрытых hardcodes;
4. dashboard визуально и семантически различает `EXPERT ESTIMATE`,
   `MEASURED ASSOCIATION` и `CAUSAL ESTIMATE`;
5. сравнение web chat / agent platform использует только matched completed jobs
   и показывает coverage;
6. residual discovery не создаёт новый сценарий из дублей или перефразировок
   известного use case;
7. passport объясняет membership и action card через метрики и примеры, а не
   через доверие к summary;
8. held-out сценарий `Email → Project ticket` устойчиво обнаруживается на
   повторных прогонах и не склеивается с общим управлением задачами;
9. CPU-only 100k stress profile укладывается в измеримый приемлемый latency/RAM
   budget либо порождает честный `coverage_warning`;
10. отсутствие timestamp, response, error, run, cost или baseline приводит к
    `N/A`, а не к синтетическим выводам;
11. default demo полностью проходит без сети и H100.

Результат red-team gate: сохранить архитектуру или точечно изменить
thresholds, run reconstruction, economic assumptions/evidence gate. Расширять
scope новыми крупными подсистемами до прохождения gate нельзя.
