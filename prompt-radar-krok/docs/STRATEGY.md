# Стратегия Prompt Radar

## 1. Рамка решения

Цель кейса - не просто разложить запросы по темам, а превратить логи ИИ-агентов
в доказуемые продуктовые решения для CTO: какие сценарии уже устойчивы, какой
новый сценарий действительно появился, где есть наблюдаемая проблема и какое
действие следует рассмотреть.

Исходные материалы задают пять критериев жюри:

1. понятность результата для CTO;
2. качество группировки;
3. интерпретируемость категорий и сценариев;
4. устойчивость, воспроизводимость и скорость;
5. креативность и продуктовая ценность.

Важное ограничение данных: файл `Темы для генерации датасета.xlsx` содержит
31 тему в `Лист1!A3:A33`, а не реальные логи КРОК. В нём нет времени, ответов
агента, ошибок, latency, feedback и организационных атрибутов. Все будущие
демо-значения на их основе должны иметь `synthetic_flag=true` и не могут
подаваться как реальные инсайты КРОК.

Интервью со стейкхолдером добавляет второй управленческий вопрос: агентской
платформой пользуется меньше людей, чем обычным LLM-веб-чатом, но она расходует
существенно больше токенов. Поэтому количество запросов, пользователей и
токенов не является единицей пользы. Каноническая бизнес-единица для экономики
- законченный `agent run` (одна цель пользователя, цепочка LLM/tool calls,
результат, проверка и доработка). Внутренние вызовы остаются диагностикой
стоимости и качества orchestration, но не считаются отдельными выполненными
задачами.

## 2. Пять существенно разных концепций

Оценки ниже - экспертная оценка до реализации, а не результаты эксперимента.
Шкала каждого критерия: от 1 до 5.

### Сравнение по критериям жюри

| Концепция | Понятность CTO | Качество группировки | Интерпретируемость | Устойчивость и скорость | Креатив / ценность | Итого |
|---|---:|---:|---:|---:|---:|---:|
| 1. Taxonomy Control Tower | 4 | 4 | 5 | 5 | 2 | 20/25 |
| 2. Pure Semantic Discovery | 3 | 4 | 3 | 3 | 4 | 17/25 |
| 3. LLM Analyst Council | 5 | 4 | 4 | 2 | 4 | 19/25 |
| 4. Workflow Graph Miner | 4 | 3 | 5 | 2 | 5 | 19/25 |
| 5. Evidence-First Opportunity Radar | 5 | 5 | 5 | 4 | 5 | 24/25 |

### 2.1. Taxonomy Control Tower

**Идея.** Заранее зафиксировать понятную многомерную таксономию
`system × intent × object × automation_mode × business_domain`, затем
multi-label классифицировать каждый запрос и строить дашборд по этим осям.

- **Классификация и новые use cases:** высокая точность на известных классах,
  но слабое обнаружение неизвестных сценариев; новые случаи часто попадут в
  ближайший существующий класс.
- **Объяснимость для CTO:** отличная; каждое решение объясняется совпавшими
  осями, примерами и уверенностью.
- **Реализуемость:** самая высокая; можно получить стабильный CPU-only baseline
  за короткий срок.
- **GPU и внешние API:** не нужны.
- **Основной риск:** результат выглядит как хороший BI-классификатор, но не
  решает главную боль поиска новых паттернов.
- **Вероятность красивого демо:** высокая, но вау-эффект ограничен.
- **Вау-фича:** интерактивный многомерный срез одного запроса по пяти бизнес-осям.

### 2.2. Pure Semantic Discovery

**Идея.** Не задавать сценарии заранее: построить эмбеддинги всех запросов,
кластеризовать их, автоматически назвать кластеры и показать карту тем.

- **Классификация и новые use cases:** хорошо находит неожиданные группы, но
  плохо гарантирует, что разные бизнес-намерения не склеятся по общей лексике.
- **Объяснимость для CTO:** средняя; красивая карта не всегда отвечает на вопрос
  «почему эти запросы вместе».
- **Реализуемость:** средняя; подбор HDBSCAN/BERTopic-параметров и борьба с
  нестабильными малыми кластерами могут съесть время.
- **GPU и внешние API:** GPU не обязателен; LLM для названий можно заменить
  extractive naming.
- **Основной риск:** при небольшом синтетическом наборе карта будет эффектной,
  но статистически хрупкой.
- **Вероятность красивого демо:** средняя: визуально сильное, но возможны
  странные кластеры прямо на защите.
- **Вау-фича:** «галактика запросов» с автоматически найденными темами.

### 2.3. LLM Analyst Council

**Идея.** Несколько LLM-ролей последовательно классифицируют запросы, предлагают
сценарии, критикуют друг друга и формируют executive summary.

- **Классификация и новые use cases:** потенциально высокая семантическая
  точность, особенно на сложных формулировках, но трудно воспроизводима.
- **Объяснимость для CTO:** высокий уровень текста, но объяснение может быть
  убедительным без достаточного статистического основания.
- **Реализуемость:** средняя/низкая из-за стоимости, latency, обработки 100k
  токенов и большого числа отказоустойчивых вызовов.
- **GPU и внешние API:** высокая зависимость от локальной большой модели или API.
- **Основной риск:** сеть, квоты, недетерминизм, prompt injection из логов и
  слишком длинный live-demo.
- **Вероятность красивого демо:** высокая при идеальном API и низкая при любой
  инфраструктурной проблеме.
- **Вау-фича:** автоматически написанный «бриф для CTO» с дебатами аналитиков.

### 2.4. Workflow Graph Miner

**Идея.** Представить каждый запрос как граф
`роль → намерение → система → объект → результат`, а use case искать как
часто повторяющийся подграф или межсистемный маршрут.

- **Классификация и новые use cases:** хорошо обнаруживает составные процессы
  вроде `Email → создать → Project ticket`, но хуже работает на одношаговых
  запросах и при неполных полях.
- **Объяснимость для CTO:** высокая; граф показывает сам бизнес-процесс.
- **Реализуемость:** низкая для хакатона: извлечение связей, нормализация графа,
  поиск подграфов и удобная визуализация требуют слишком много времени.
- **GPU и внешние API:** GPU не обязателен, но качественное извлечение графа
  часто тянет за собой LLM.
- **Основной риск:** эффектная, но недоделанная схема без доказанного качества
  группировки.
- **Вероятность красивого демо:** средняя.
- **Вау-фича:** карта межсистемных автоматизаций и «разрывов» процесса.

### 2.5. Evidence-First Opportunity Radar

**Идея.** Разделить поток на известные, новые и неопределённые сценарии.
Сначала запрос получает устойчивые бизнес-оси, затем только остаток с низкой
уверенностью проходит поиск новых кластеров. Новый сценарий показывается CTO
только вместе с «паспортом доказательств»: поддержка, связность, отличие от
известных сценариев, устойчивость на перезапусках и реальные примеры запросов.

- **Классификация и новые use cases:** сочетает сильную классификацию известных
  случаев с контролируемым поиском нового; abstention не позволяет насильно
  разнести всё по классам.
- **Объяснимость для CTO:** максимальная; любое название, тренд и действие можно
  раскрыть до метрик и примеров.
- **Реализуемость:** высокая при строгом ограничении scope: одна таксономия,
  один residual-discovery pipeline и один executive dashboard.
- **GPU и внешние API:** baseline работает на CPU и без сети; LLM допустима
  только как заменяемый модуль именования кластеров.
- **Основной риск:** пороги novelty/stability требуют аккуратной калибровки, а
  при малом наборе часть данных честно останется `unresolved`.
- **Вероятность красивого демо:** высокая: есть понятный сюжет рождения нового
  сценария и drill-down до доказательств.
- **Вау-фича:** **«Паспорт нового сценария»** - не просто облако точек, а
  проверяемое доказательство, почему сценарий существует и какое действие он
  оправдывает.

## 3. Выбор

Выбран вариант **Evidence-First Opportunity Radar**.

Причина выбора: он напрямую закрывает все пять критериев и не заставляет
выбирать между предсказуемой таксономией и поиском нового. При этом это не
«комбайн из всех идей»: продукт строится вокруг одного решения - допускать
use case на экран CTO только после прохождения evidence gate. Графовый анализ,
LLM-совет и сложная real-time платформа сознательно не входят в первую версию.
Поверх доказанного use case добавляется только связанный с ним run-level слой
unit economics; причинный ROI без измеренного baseline по-прежнему не
заявляется.

## 4. Product thesis

**Prompt Radar превращает поток запросов и законченных agent runs в очередь
доказанных продуктовых возможностей: он стабильно размечает известные
сценарии, не прячет неизвестные в ближайшую категорию, выдаёт новому паттерну
паспорт доказательств и показывает CTO, превращаются ли затраты на этот use
case в завершённую работу, экономию времени и положительную unit economics.
Экспертная оценка ценности всегда отделена от измеренного causal effect, а
следующее действие - развивать, оптимизировать, исследовать или остановить -
опирается на evidence и явно показанные assumptions.**

## 5. Главная демонстрационная история

На основе одной из предоставленных тем создаётся **явно синтетический** новый
поток запросов: «создание тикетов Project из входящих писем». Оси `Email`,
`Project`, `create`, `task` уже известны, но самого use case нет в каталоге
известных сценариев. Radar не приписывает эти запросы к обычному «управлению
задачами», а формирует устойчивый residual-кластер и показывает его паспорт.
Затем несколько внутренних LLM/tool events сворачиваются в один synthetic
`agent run`, и CTO видит не «ценность токенов», а стоимость завершённой задачи,
ручную проверку, rework и диапазон net value.

Это сильная история, потому что она одновременно демонстрирует:

- корректную multi-label классификацию межсистемного запроса;
- обнаружение нового use case без заранее заданного названия;
- понятное автоматизационное действие;
- доказательства вместо декоративной карты эмбеддингов;
- отсутствие двойного счёта внутренних LLM-вызовов;
- экран «ценность против стоимости» с low/base/high assumptions;
- честную маркировку синтетической динамики.

## 6. Архитектура

### 6.1. Один end-to-end поток

```text
CSV / JSONL / Parquet / demo generator
  -> schema validation и маркировка происхождения
  -> reconstruction: events -> один agent run / completed job
  -> PII masking, нормализация, дедупликация
  -> long-input sketch
  -> multi-axis classifier с abstention
  -> известный use-case matcher
  -> residual pool
  -> constrained clustering + stability gate
  -> extractive/optional local naming
  -> run success + cost ledger + baseline/sensitivity
  -> evidence passport + value/cost action card
  -> агрегаты и executive dashboard
```

### 6.2. Слои

#### A. Ingestion и provenance

- Принимаются реальные логи или синтетический генератор.
- Каждая строка получает `dataset_kind`, `synthetic_flag`, `source_topic_id` и
  версию схемы.
- События одного исполнения связываются по `run_id`; пользовательская цель,
  внутренние LLM-вызовы и tool calls не образуют самостоятельные бизнес-задачи.
- Отсутствующие timestamp/response/error не заполняются выдуманными значениями.
- Демо-набор хранится отдельно от любого будущего реального набора.

#### B. Безопасная предобработка

- Маскирование email, телефонов, идентификаторов и имён до эмбеддингов.
- Нормализация пробелов и повторов без переписывания смысла.
- Exact/near-duplicate detection, чтобы копии одного запроса не создавали
  искусственный «новый сценарий».
- Текст лога всегда считается недоверенными данными: инструкции из него не
  исполняются, а при LLM-наименовании передаются только как quoted evidence.

#### C. Long-input sketch

- Цель запроса отделяется от приложенного контекста, если лог хранит роли,
  вложения или границы сообщений.
- Для обычного запроса строится один эмбеддинг.
- Для длинного запроса строится ограниченный semantic sketch из обязательных
  instruction-сегментов и не более 24 репрезентативных чанков.
- В результат пишутся `request_token_count`, `chunks_total`,
  `chunks_selected`, `long_input_mode` и `coverage_warning`.

#### D. Многомерная классификация

Фиксируется версия таксономии:

- `system`: Email, CRM, Jira, ИСУП, Project, Calendar, Confluence, Excel,
  CoolFeedback, OpenWeb, Other;
- `intent`: search, summarize, create, update, reply, export, monitor, notify,
  schedule, explain;
- `object`: email, client, deal, tender, task, project, meeting, room, document,
  employee_note, report;
- `automation_mode`: one_shot, recurring, monitoring, notification;
- `business_domain`: sales, projects, HR, knowledge, productivity;
- `use_case`: конкретный человекочитаемый сценарий.

Классификация multi-label. Для каждой оси сохраняются confidence и evidence
chunks. Если confidence ниже порога, ставится `abstain`, а не случайная метка.

#### E. Известные и новые сценарии

1. Сначала запрос сопоставляется с прототипами известных use cases.
2. Высокоуверенные совпадения не кластеризуются заново.
3. Низкоуверенные запросы попадают в residual pool.
4. Residual pool делится хотя бы по крупному `business_domain/system`, чтобы
   лексически похожие, но бизнес-разные запросы не склеивались.
5. Кластер-кандидат проходит несколько bootstrap/seed прогонов.
6. Он становится `emerging` только при выполнении всех условий:
   достаточная поддержка, внутренняя связность, отличие от известных
   прототипов и устойчивое ядро.
7. Всё остальное остаётся `unresolved`; это нормальный и видимый исход.

#### F. Именование и саммари

- Default: воспроизводимое extractive name из осей, ключевых фраз и medoid.
- Optional: локальная небольшая instruct-модель получает только redacted
  medoid-примеры и возвращает строгое JSON-имя/саммари.
- Название LLM не влияет на membership кластера.
- Любое имя можно раскрыть до типовых и граничных примеров.

#### G. Evidence passport

Паспорт содержит:

- название и статус `known / emerging / unresolved`;
- объём и долю с явным знаменателем;
- cohesion и distinctness;
- stability ядра по повторным прогонам;
- три redacted medoid-примера и два boundary-примера;
- multi-axis профиль;
- доступную динамику или честное `N/A`;
- доступные failure-сигналы или честное `N/A`;
- action card, правило её формирования и необходимые оговорки.

#### H. Action cards

Рекомендации формируются прозрачными правилами, а не свободным текстом LLM:

- `SCALE / AUTOMATE`: устойчивый повторяющийся сценарий, достаточный объём, высокая
  успешность, низкая вариативность шагов и положительный conservative net value;
- `OPTIMIZE_COST`: ценность положительна, но model/tool cost, retry или loops
  оставляют измеримый потенциал оптимизации;
- `IMPROVE_AGENT`: есть подтверждённая доля технических ошибок или негативный
  feedback, rework либо дорогие retry/loop-паттерны на устойчивом сценарии;
- `TRAIN_USERS`: много низкоуверенных/повторных формулировок при работающем
  агенте;
- `VALIDATE`: base-case положителен, но evidence level или low-case не
  позволяет утверждать эффект;
- `INVESTIGATE`: новый или неоднозначный кластер без достаточного evidence;
- `WATCH`: сценарий устойчив, но данных пока недостаточно для действия.

Система не заявляет денежный ROI или сэкономленные часы без соответствующих
полей и не переводит expert baseline в causal claim.

#### I. Run-level unit economics

- Все внутренние model/tool costs суммируются один раз на `run_id`.
- Отдельно считаются marginal cost и fully-loaded cost с долей командных затрат.
- Gross value строится от человеческого baseline, success/quality и ставки
  труда, а не от количества токенов.
- User active time, review и rework уменьшают net saved time и входят в
  человеческую стоимость agent run.
- Expert baseline даёт только `estimated` economics с low/base/high диапазоном.
- `causal_estimate` разрешён только после time study, paired/control experiment
  или квазиэкспериментального сравнения.

### 6.3. Рекомендуемый технологический контур

- Python pipeline, конфигурация в YAML/JSON, фиксированные random seeds.
- Локальный multilingual sentence encoder малого размера.
- CPU-friendly clustering; GPU только ускоряет batch embeddings.
- DuckDB/Parquet для воспроизводимых локальных агрегатов.
- Streamlit как самый быстрый путь к сильному интерактивному демо.
- Версионирование `schema`, `taxonomy`, `embedding_model`, `thresholds`,
  `cluster_run` и `dataset`.

Это архитектурное решение, а не разрешение начинать реализацию на этом этапе.

## 7. Модель данных

Главная сущность для бизнес-метрик - `agent_run`. `request_event`, внутренние
LLM-вызовы и tool calls являются дочерними событиями run и не увеличивают число
выполненных задач. Классификация может использовать текст цели и запросов, но
агрегация success, cost, saved time и ROI всегда выполняется по `run_id`.

### 7.1. `request_event`

| Поле | Обязательность | Смысл |
|---|---|---|
| `request_id` | да | Стабильный идентификатор запроса |
| `run_id` | да для agent product | Родительский agent run |
| `event_time` | нет | Время; без него динамика недоступна |
| `user_id_hash` | нет | Обезличенный пользователь |
| `department` | нет | Организационный срез |
| `agent_id` | да | Агент/продукт |
| `source_system` | нет | Система-источник |
| `instruction_text` | да | Пользовательская цель |
| `context_text` / `context_ref` | нет | Приложенный длинный контекст |
| `request_token_count` | да | Реально измеренная длина |
| `response_text` | нет | Ответ агента |
| `latency_ms` | нет | Измеренная задержка |
| `success` | нет | Явный сигнал исполнения |
| `error_type` | нет | Наблюдаемая ошибка |
| `retry_count` | нет | Повторные попытки |
| `feedback` | нет | Явная оценка пользователя |
| `synthetic_flag` | да | Защита от смешения синтетики и фактов |
| `source_topic_id` | нет | Связь с одной из 31 исходных тем |
| `dataset_version` | да | Воспроизводимость |

### 7.2. `request_analysis`

| Поле | Смысл |
|---|---|
| `request_id` | Связь с событием |
| `taxonomy_version` | Версия категорий |
| `labels` | Multi-label значения по осям |
| `label_confidences` | Уверенность по каждой оси |
| `abstain_axes` | Оси без достаточной уверенности |
| `evidence_chunks` | Фрагменты, повлиявшие на решение |
| `embedding_model_version` | Версия представления |
| `long_input_mode` | Обычный / hierarchical sketch |
| `pii_redaction_count` | Контроль предобработки |
| `quality_risk` | Риск непонимания, не «поломка» |

### 7.3. `scenario` и `scenario_membership`

`scenario` хранит `scenario_id`, имя, summary, статус, родительские оси,
support, cohesion, distinctness, stability, discovery_window, naming_method,
версию алгоритма и список evidence IDs.

`scenario_membership` хранит `request_id`, `scenario_id`,
`membership_confidence`, `is_medoid`, `is_boundary` и `cluster_run_id`.

### 7.4. `scenario_window_metric`

Хранит окно времени, объём, долю, абсолютное изменение, темп роста,
confirmed-failure rate, probable-failure rate, abstention rate и знаменатель
каждой метрики. Строка создаётся только для доступных исходных сигналов.

### 7.5. `action_card`

Хранит `action_type`, `rule_id`, краткое обоснование, supporting metrics,
evidence IDs, confidence, ограничения данных и `synthetic_flag`.

### 7.6. `agent_run`

| Поле | Смысл |
|---|---|
| `run_id` | Одна пользовательская цель / completed job |
| `job_id` | Общий идентификатор сопоставимой задачи между продуктами |
| `product_surface` | `web_chat` или `agent_platform` |
| `user_id_hash`, `department`, `agent_id` | Организационный контекст |
| `goal_text` | Нормализованная цель пользователя |
| `use_case_id` | Результат классификации/discovery |
| `started_at`, `ended_at`, `elapsed_ms` | Полная длительность выполнения |
| `run_status` | `success / partial / failed / cancelled` |
| `success_weight` | Наблюдаемый вес результата: 1 / настраиваемый partial / 0 |
| `quality_score` | Приемлемость результата относительно критерия задачи |
| `validation_method` | Tool check, human review, feedback или proxy |
| `llm_call_count`, `tool_call_count` | Диагностика orchestration |
| `retry_count`, `loop_detected` | Признаки неэффективного выполнения |
| `input_tokens`, `output_tokens`, `cached_tokens` | Драйвер стоимости, не пользы |
| `user_active_minutes` | Активное время пользователя во время run |
| `human_review_minutes` | Проверка результата |
| `rework_minutes` | Исправление/повторная ручная работа |
| `synthetic_flag`, `dataset_version` | Provenance |

### 7.7. `run_step` и `cost_ledger`

`run_step` хранит `step_id`, `run_id`, тип `llm/tool/human`, модель или
инструмент, start/end, status, error, attempt, tokens и tool latency. Он нужен
для диагностики дорогих циклов, но не считается бизнес-задачей.

`cost_ledger` хранит:

- `run_id`, `cost_type` (`model_input`, `model_output`, `tool_api`,
  `infrastructure`, `team_allocation`, `human_touch`);
- количество, unit rate, currency, price-book version и период;
- `model_cost`, `tool_cost`, `infrastructure_cost`,
  `amortized_team_cost`, `human_touch_cost`;
- метод распределения фиксированных затрат и источник ставки.

Для MVP командные расходы распределяются равной долей на все started
production runs периода. В sensitivity analysis дополнительно показывается
вариант без fixed team cost, чтобы не смешивать решение «запускать ещё один
run» с портфельным вопросом «окупается ли вся платформа».

### 7.8. `baseline_assumption`

| Поле | Смысл |
|---|---|
| `use_case_id` | Сценарий, к которому относится baseline |
| `baseline_low/base/high_minutes` | Диапазон времени ручного выполнения |
| `baseline_source` | Expert estimate, time study, paired или control |
| `baseline_confidence_level` | `E0 / E1 / E2 / E3` |
| `success_probability_low/base/high` | Прогноз успеха для portfolio view |
| `quality_coefficient_low/base/high` | Поправка на приемлемость результата |
| `labor_cost_low/base/high_per_minute` | Полная ставка и её источник |
| `cost_allocation_method` | Способ распределения infra/team cost |
| `quality_threshold` | Что считается приемлемым результатом |
| `valid_from`, `valid_to`, `owner` | Версия и ответственность |
| `assumption_notes` | Ограничения применимости |

Лестница доказательности:

- `E0 expert_proxy` - экспертные минуты; только сценарный estimate;
- `E1 observed_time_study` - измеренное время без контрольной группы;
- `E2 paired_tasks` - одинаковые задачи с агентом и без него;
- `E3 causal_estimate` - рандомизированная/валидная контрольная или
  квазиэкспериментальная оценка.

### 7.9. Формулы unit economics

Для одного run:

```text
B = baseline_human_minutes
A = user_active_minutes
V = human_review_minutes
W = rework_minutes
s = observed success_weight
q = quality_coefficient
r = labor_cost_per_minute

raw_net_saved_minutes = B - A - V - W
realized_net_saved_minutes = B × s × q - A - V - W

gross_value = B × r × s × q
human_touch_cost = (A + V + W) × r

agent_cost_marginal =
    model_cost
    + tool_cost
    + infrastructure_cost
    + human_touch_cost

agent_cost_fully_loaded =
    agent_cost_marginal
    + amortized_team_cost

net_value_marginal = gross_value - agent_cost_marginal
ROI_marginal = net_value_marginal / agent_cost_marginal
value_cost_ratio_marginal = gross_value / agent_cost_marginal

net_value_fully_loaded = gross_value - agent_cost_fully_loaded
ROI_fully_loaded = net_value_fully_loaded / agent_cost_fully_loaded
value_cost_ratio_fully_loaded = gross_value / agent_cost_fully_loaded
```

В ретроспективном расчёте `s` - наблюдаемый status run. В portfolio forecast
`s` заменяется на эмпирическую `P(success | use_case)` с интервалом; плановая
вероятность никогда не подменяет фактическую completion rate.

`realized_net_saved_minutes` и оба `net_value` не обрезаются снизу нулём:
неудачный run должен показывать отрицательную ценность. ROI не выводится при
нулевом знаменателе. Для capacity:

```text
FTE_capacity_equivalent =
    sum(realized_net_saved_minutes)
    / work_minutes_per_FTE_in_period
```

Это эквивалент высвобождённой мощности, а не обещание сокращения headcount.

На `E0/E1` результат публикуется как `estimated` и всегда с low/base/high
диапазоном по baseline, success/quality, labor rate и cost allocation. На
`E2/E3` для разницы времени и net value показывается 95% confidence interval.

### 7.10. Synthetic generator для run economics

Генератор создаёт не независимые случайные колонки, а согласованную иерархию:

```text
job
  -> agent_run
      -> request events
      -> llm calls
      -> tool calls
      -> validation
      -> review/rework
      -> cost ledger
      -> baseline assumptions
```

Обязательные синтетические поля: `run_id`, `job_id`, `product_surface`,
`run_status`, `validation_method`, `llm_call_count`, `tool_call_count`,
`tool_error_count`, `retry_count`, input/output/cached tokens, model/tool/infra
costs, active/review/rework minutes, baseline low/base/high, baseline source,
labor rate, quality score и `synthetic_flag=true`.

Зависимости должны быть правдоподобны: retry/loops увеличивают tokens, cost и
elapsed time; ошибки tool calls повышают partial/failure и rework; сложные use
cases имеют более высокий baseline; successful first-pass runs требуют меньше
review. Ни одно число генератора не становится утверждением о КРОК.

### 7.11. Сравнение web chat и agent platform

Сравниваются только сопоставимые `job_id/use_case` и одинаковый quality
threshold. Для web chat сообщения объединяются в одну сессию-задачу; для
agent platform все внутренние события объединяются в `run_id`.

Срезы сравнения:

- completed и quality-validated jobs;
- completion и first-pass yield;
- net saved minutes на completed job;
- marginal/fully-loaded cost на completed job;
- cost per successful job;
- net value и value/cost ratio на 100 сопоставимых задач;
- coverage - доля задач, для которых сравнение вообще корректно.

Числа 1300 и 150 пользователей и расход токенов показываются только как
контекст масштаба. Коэффициент веб-чата `0.3 / 1 / 2` применяется один раз к
сессии-задаче как expert proxy и никогда не применяется к внутренним agent
calls.

## 8. Demo flow на 3-5 минут

### Экран «Ценность против стоимости»

Главный executive screen поверх сценариев:

- KPI cards: completed runs, validated success, gross value, marginal и
  fully-loaded cost, net value, ROI range и FTE capacity equivalent;
- bubble chart по use cases: X - cost per successful run, Y - realized net value
  per run, размер - completed runs, цвет - evidence level `E0-E3`;
- квадранты `SCALE`, `OPTIMIZE COST`, `VALIDATE`, `FIX/STOP`;
- переключатель `low / base / high` и видимый assumptions drawer;
- drill-down из use case в run passport: steps, retry/loops, cost ledger,
  baseline, review/rework и validation evidence;
- постоянные бейджи `SYNTHETIC`, `EXPERT ESTIMATE` или `CAUSAL ESTIMATE`.

Высокий расход токенов считается оправданным только если run завершает
quality-validated задачу и conservative `value_cost_ratio > 1` при приемлемых
latency/rework. Если base-case положителен, но low-case отрицателен, статус -
`VALIDATE`; если даже high-case отрицателен - `FIX/STOP`. Tokens per run служат
диагностикой стоимости и циклов, но не показателем пользы.

### 0:00-0:35 - честный вход

Показать экран импорта: «31 исходная тема, реальные временные метки и ответы не
предоставлены». Выбрать synthetic demo dataset, построенный из этих тем.
На экране всегда виден бейдж `SYNTHETIC DEMO`.

### 0:35-1:10 - executive radar

Показать топ известных сценариев и один новый кандидат. Не задерживаться на
общем дашборде; сразу открыть карточку
«Создание тикетов Project из входящих писем».

### 1:10-2:05 - паспорт нового сценария

Показать:

- оси `Email + Project / create / task / one_shot`;
- поддержку, cohesion, distinctness и stability;
- три непохожие формулировки, которые всё равно попали вместе;
- ближайший известный сценарий и объяснение, почему кластер отделён;
- статус `emerging`, а не безусловный «истинный класс».

Это центральный вау-момент.

### 2:05-3:20 - ценность против стоимости

Показать, как десятки synthetic LLM/tool calls свёрнуты в один `agent run`.
Открыть экран value/cost для найденного use case:

- success/partial/failure и first-pass yield;
- model/tool/infra/human-touch costs;
- baseline low/base/high и уровень доказательности `E0`;
- review/rework и realized net saved minutes;
- marginal и fully-loaded net value/ROI range.

Переключить base на low. Action card меняется с `AUTOMATE` на `VALIDATE`, если
консервативный сценарий не подтверждает положительную ценность. Это не
демонстрация реального ROI КРОК, а демонстрация корректной экономической модели.

### 3:20-4:10 - честность про данные

Переключить источник на исходный Excel:

- график динамики становится `N/A: timestamp отсутствует`;
- «сломанные запросы» становятся `N/A: нет response/error/feedback`;
- economics становится `N/A: нет run/cost/baseline telemetry`;
- низкая уверенность остаётся отдельным `quality_risk`, а не ошибкой агента.

Затем вернуть synthetic demo и показать, что искусственные timestamps и
telemetry явно помечены, а expert baseline не назван causal effect.

### 4:10-4:45 - техническое завершение

Включить `CPU-only / offline`, повторить запуск на том же наборе и показать
совпадающий run fingerprint. Финальная фраза: «Radar не только находит тему, он
доказывает, что это сценарий, сворачивает внутренние вызовы в завершённую
задачу и показывает, превращается ли её стоимость в проверяемую ценность».

## 9. Метрики и evaluation contract

Все результаты публикуются раздельно для:

1. hand-labeled challenge set;
2. held-out synthetic set;
3. реальных логов, если они будут предоставлены.

Синтетические показатели никогда не смешиваются с реальными.

### 9.1. Классификация

- macro-F1 и micro-F1 по каждой оси;
- Hamming loss для multi-label;
- exact-match ratio по набору осей;
- coverage при заданном пороге abstention;
- Expected Calibration Error или reliability bins;
- отдельный score на cross-system и long-input поднаборах.

Предварительный gate: macro-F1 не ниже 0.80 на held-out synthetic, ни одна
ключевая ось не ниже 0.70; показатели подтверждаются отдельно на небольшой
ручной challenge-выборке. Это целевой gate, не достигнутый результат.

### 9.2. Группировка

- B-cubed precision/recall/F1;
- pairwise F1;
- Adjusted Rand Index против ручной разметки;
- cluster purity без использования purity как единственной метрики;
- доля `unresolved`, чтобы качество не улучшалось скрытым отбрасыванием.

Предварительный gate: B-cubed F1 не ниже 0.75 и отсутствие очевидного
cross-domain merge на ручной проверке.

### 9.3. Обнаружение новых use cases

- precision/recall/F1 для `known vs novel`;
- precision@k кандидатов, показанных CTO;
- stability ядра: Jaccard membership по bootstrap-прогонам;
- distinctness от ближайшего известного прототипа;
- minimum support и доля шума.

Предварительный gate: precision новых сценариев не ниже 0.70, stability ядра не
ниже 0.80; recall вторичен, потому что ложная «новая возможность» опаснее
пропущенного слабого сигнала.

### 9.4. Интерпретируемость и продуктовость

- human rating названия и summary по шкале 1-5;
- доля карточек, где эксперт может восстановить причину решения по evidence;
- actionability rating CTO/product owner;
- время от открытия карточки до выбора следующего действия;
- доля рекомендаций с явными метриками и знаменателями.

Целевой gate: не менее 4/5 за понятность имени и не менее 90% action cards с
полным evidence trail.

### 9.5. Технические метрики

- p50/p95 latency для обычного и 100k-token профиля отдельно;
- throughput и peak RAM на CPU;
- время batch-run и объём cache hits;
- идентичность классификации при повторном запуске;
- ARI/Jaccard между фиксированными повторными cluster runs;
- доля запросов с `coverage_warning`;
- число внешних сетевых вызовов в default demo: **0**.

Предварительный gate: p95 до 2 секунд для обычного запроса и до 8 секунд для
100k-token sketch на контрольной CPU-машине; одинаковый run fingerprint при
повторном запуске с неизменными версиями. Значения должны быть измерены, а не
заявлены заранее как факт.

### 9.6. Успешность agent run

- run completion rate;
- full / partial / failed / cancelled rate;
- quality-validated success rate;
- first-pass yield: success без retry и rework;
- tool-call success и error rate как диагностика, не бизнес-знаменатель;
- retry rate и loop rate;
- human intervention, review и rework rate;
- median/p95 elapsed time, user active time и review time;
- cost per started, completed и quality-validated run;
- доля runs с достаточной telemetry для расчёта.

Главный знаменатель бизнес-успеха - started agent runs, а не LLM calls.
`validated success` показывается отдельно от технического `run_status=success`.

### 9.7. Экономика и неопределённость

- gross value, marginal/fully-loaded agent cost и net value;
- raw и realized net saved minutes на run/use case;
- value/cost ratio и ROI с указанием cost mode;
- cost per successful job;
- FTE capacity equivalent с видимым количеством рабочих минут в периоде;
- доля стоимости в model/tool/infra/human-touch/team components;
- sensitivity low/base/high и ширина диапазона;
- доля value, основанная на `E0/E1/E2/E3`;
- для paired/control data: mean/median treatment effect, 95% CI, quality delta
  и доля неуспешных задач.

Decision rule для `SCALE`: quality-validated success достаточен, conservative
net value положителен, нижняя граница value/cost ratio выше 1, а доля runs с
полной telemetry превышает заранее установленный gate. Пока baseline `E0`,
карточка может рекомендовать только `VALIDATE`, `WATCH` или
`OPTIMIZE COST`, но не утверждать доказанный ROI.

## 10. Must-have

- строгий data contract и provenance;
- генератор synthetic logs из 31 темы с явной маркировкой;
- PII masking и защита от инструкций внутри логов;
- multi-axis классификация с confidence и abstention;
- известный use-case matching;
- residual clustering с novelty/stability gate;
- passport одного нового сценария с evidence;
- понятные названия, summary и примеры;
- action cards на прозрачных правилах;
- reconstruction событий в один `agent_run` без двойного счёта LLM/tool calls;
- run success, validation, review/rework и cost ledger;
- baseline assumptions с `E0-E3` и low/base/high;
- gross value, marginal/fully-loaded cost, net value и ROI range;
- экран «ценность против стоимости» и сравнение продуктов по completed jobs;
- корректное `N/A` для недоступной динамики и failure metrics;
- корректное `N/A` для отсутствующих run/cost/baseline данных;
- offline CPU-only demo;
- evaluation report с разделением synthetic/hand-labeled/real;
- воспроизводимый run fingerprint.

## 11. Consciously not doing

- не обучаем собственную большую LLM и не делаем fine-tuning LLM;
- не вызываем LLM для каждого запроса;
- не зависим от внешнего API в default demo;
- не считаем внутренние LLM-вызовы самостоятельными бизнес-задачами;
- не используем токены, пользователей или запросы как прямую метрику пользы;
- не строим графовый майнер бизнес-процессов в первой версии;
- не делаем multi-agent «совет аналитиков»;
- не обещаем real-time streaming: batch refresh достаточно для защиты;
- не выдаём expert baseline и synthetic economics за измеренный causal effect;
- не показываем денежный ROI без assumptions, диапазона и cost mode;
- не сравниваем 1300 web-chat и 150 agent users без matched completed jobs;
- не называем низкую уверенность классификатора «поломкой агента»;
- не показываем синтетическую динамику как данные КРОК;
- не строим сложный редактор таксономии и полноценную MLOps-платформу;
- не добавляем чат с дашбордом, если он не улучшает конкретную метрику жюри.

## 12. План реализации по приоритетам

### P0 - доказуемый вертикальный срез

1. Зафиксировать schema, taxonomy v1 и правила synthetic provenance.
2. Зафиксировать `agent_run -> events/steps/cost ledger` и правила дедупликации
   внутренних вызовов.
3. Создать hand-labeled challenge set и synthetic generator из 31 темы с
   согласованными tool calls, failures, costs, review/rework и baseline ranges.
4. Сделать CPU baseline multi-axis классификации с abstention.
5. Реализовать known use-case matching и метрики классификации.
6. Собрать один executive экран и drill-down до запросов/runs.

**Gate P0:** одна цель проходит путь от ingestion до объяснимой карточки и
одного reconciled `agent_run`; внутренние вызовы не удваивают business volume
или gross value.

### P1 - победная фича

1. Выделить residual pool.
2. Добавить constrained clustering и повторные stability runs.
3. Реализовать паспорт сценария.
4. Настроить held-out сценарий «Email → Project ticket» для честной проверки
   novelty detection.
5. Добавить value/cost passport и rule-based action card с sensitivity.

**Gate P1:** новый сценарий проходит evidence gate и воспроизводится при
повторном запуске; соседние известные сценарии не склеиваются; base/low
assumptions способны изменить рекомендацию без изменения исходных событий.

### P2 - спорные требования и доверие

1. Реализовать long-input sketch и отдельный benchmark 100k.
2. Развести confirmed failure, probable failure и quality risk.
3. Реализовать динамику с data-availability gate.
4. Добавить экран сравнения web chat / agent platform только по matched jobs.
5. Добавить CPU/GPU profiles с одинаковой семантикой результата.
6. Зафиксировать run fingerprint и offline demo cache.

**Gate P2:** демо не ломается без сети и H100; при отсутствии telemetry честно
показывает `N/A`; expert economics везде подписана как estimate.

### P3 - только если P0-P2 зелёные

- локальная LLM для улучшения имени/summary с extractive fallback;
- дополнительные executive-срезы по agent/department;
- bootstrap CI для реального paired/control pilot после появления данных;
- экспорт evidence report в Markdown/PDF;
- точечная визуальная полировка.

## 13. Точные решения по спорным требованиям

### 13.1. «Средний запрос 100k токенов»

Решение: трактовать 100k как **обязательный нагрузочный профиль**, но не как
доказанный средний размер реальных логов.

Алгоритм:

1. если формат лога разделяет сообщения и вложения, классифицировать прежде
   всего пользовательскую инструкцию, а контекст хранить отдельно;
2. если границ нет, разбить текст структурно на чанки около 512 токенов с
   небольшим overlap;
3. всегда взять instruction-like начало/конец и вопросительные/императивные
   сегменты;
4. дополнить их разнообразными релевантными чанками до жёсткого лимита 24;
5. агрегировать chunk embeddings по осям через top-k evidence, а не усреднять
   весь 100k-текст в один вектор;
6. сохранить coverage metadata; при слабом покрытии поставить
   `coverage_warning`, а не завышенную уверенность;
7. отдельно измерить latency/RAM на синтетическом 100k stress set.

Полный 100k-текст не отправляется во внешнюю LLM и не хранится в prompt
именования кластера.

### 13.2. Ограничение H100

Решение: **семантический baseline CPU-first**.

- Нет обучения большой модели.
- Нет обязательного GPU.
- H100, если доступна, используется только для ускорения batch embeddings или
  опционального локального naming-модуля.
- `compute_profile=cpu|cuda` меняет batch size и скорость, но не taxonomy,
  thresholds и бизнес-логику.
- Default demo запускается offline на CPU с заранее прогретыми локальными
  артефактами.
- Внешний API не является частью критического пути.

### 13.3. Динамика

Решение: динамика существует только при `event_time`.

- Для исходного Excel интерфейс показывает `N/A`, а не пустой или выдуманный
  график.
- Для synthetic demo timestamps генерируются явно и сохраняются с
  `synthetic_flag=true`.
- Сравниваются равные окна; показываются текущий объём, предыдущий объём,
  абсолютная дельта и доля.
- Если предыдущий объём равен нулю, выводится `NEW`, а не бесконечный процент.
- Тренд не публикуется при малой поддержке; показывается `insufficient data`.
- Реальные и синтетические серии никогда не агрегируются вместе.

### 13.4. «Сломанные» запросы

Решение: разделить три разных явления.

1. **Confirmed failure** - `success=false`, явный `error_type`, exception или
   timeout из telemetry.
2. **Probable failure** - сочетание повторной попытки, негативного feedback и/или
   аномальной latency. Это прокси и всегда подписано как вероятная неудача.
3. **Quality risk** - низкая уверенность классификации, противоречивые намерения
   или недостаточный контекст. Это риск понимания, а не доказательство поломки.

При наличии только текста запроса допустим только `quality_risk`. Failure rate
не считается и показывается как `N/A: нет наблюдаемого исхода`. В action card
всегда видны правило, числитель и знаменатель.

### 13.5. Единица анализа и двойной счёт

Решение: `agent_run` начинается с одной пользовательской цели и заканчивается
терминальным status либо явным timeout/cancel. Повторный orchestration внутри
того же run увеличивает cost/retry, но не business volume. Новый run создаётся
только при новой пользовательской цели или явно начатом повторном выполнении;
для повторов сохраняется `parent_run_id`.

Классификация request/step наследуется и агрегируется в use case, но:

```text
business_task_count = distinct(run_id)
gross_value_counted_once_per = run_id
agent_cost = sum(all child events for run_id)
```

Run без результата входит в started-run denominator и может иметь отрицательный
net value. Это предотвращает завышение пользы дорогими неуспешными циклами.

### 13.6. Expert baseline, causal effect и sensitivity

Решение: существующая методика
`request_count × expert_minutes × 0.3/1/2` сохраняется только как baseline для
web-chat sessions и источник `E0`. Для agent platform экспертные минуты
применяются один раз к completed job/use case, а не к каждому внутреннему
вызову.

- `estimated economics`: `E0/E1`, всегда low/base/high;
- `measured association`: наблюдаемый time study без контроля;
- `causal estimate`: `E2/E3` после paired/control design.

Для expert model показывается sensitivity по baseline minutes, labor rate,
success/quality, review/rework и fixed-cost allocation. Для измеренного
сравнения строится 95% CI разницы времени и net value. Если диапазон пересекает
ноль или value/cost ratio пересекает 1, выводится `INCONCLUSIVE`, а не
положительный ROI.

### 13.7. Когда высокий расход токенов оправдан

Решение: токены не оцениваются изолированно.

- **Оправдан:** quality-validated run завершает дорогую человеческую задачу,
  conservative marginal value/cost выше 1, review/rework приемлемы, нет
  аномального retry/loop.
- **Нужно оптимизировать:** net value положителен, но cost per successful run
  растёт из-за модели, повторов, лишних tool calls или длинного контекста.
- **Нужно валидировать:** base-case положителен, но low-case не подтверждает
  ценность либо baseline только `E0`.
- **Не оправдан:** даже high-case отрицателен, completion/quality низки или
  токены тратятся преимущественно в failed/retry loops.

Web chat и agent platform сравниваются на 100 matched completed jobs одного use
case и quality threshold. Users, messages и tokens остаются контекстом, а не
знаменателем пользы.

### 13.8. План дальнейшей валидации

1. **Instrumentation.** Связать user goal, `run_id`, steps, outcome, validation,
   active/review/rework time и cost ledger. Проверить reconciliation: сумма
   child costs равна run cost, один run даёт не более одной единицы gross value.
2. **Time study.** Для стратифицированной выборки use cases измерять ручное
   время, agent-assisted time, review/rework и качество результата. Это
   улучшает baseline до `E1`, но ещё не доказывает причинность.
3. **Paired crossover tasks.** Один набор задач выполняется с агентом и без
   агента, порядок рандомизируется, качество оценивается по единому rubric
   независимо от режима. Primary endpoint - time to acceptable result;
   secondary - quality, failure/rework и total cost.
4. **Контрольный pilot.** Если возможно, использовать рандомизацию,
   stepped-wedge rollout или matched control по роли/use case. Неуспешные runs
   сохраняются в анализе, чтобы не получить survivorship bias.
5. **Статистика.** Размер выборки определяется power analysis. Эффект
   оценивается с кластеризацией по сотруднику/типу задачи и bootstrap/robust 95%
   CI. Отдельно публикуются heterogeneity по use case и evidence coverage.
6. **Обновление assumptions.** `E0` заменяется `E1/E2/E3` только после
   документированной проверки; версии baseline и price book сохраняются.

## 14. Gate 1: архитектурный вердикт

**Вердикт: PASS WITH CONDITIONS.**

Выбранная Evidence-First Opportunity Radar сохраняется. Интервью не требует
новой стратегии: run-level unit economics является узким управленческим слоем
поверх обязательных classification/discovery и использует тот же use case
passport. Стратегия допускается к red-team, но не к заявлению доказанного ROI.

До начала основной реализации red-team должен попытаться опровергнуть
следующие утверждения:

1. reconstruction гарантирует одну бизнес-задачу и одну запись gross value на
   `run_id`, независимо от числа LLM/tool calls;
2. failure/partial runs не исчезают из denominator и способны сделать net value
   отрицательным;
3. low/base/high assumptions и marginal/fully-loaded cost меняют вывод
   прозрачно, без скрытых hardcodes;
4. web chat и agent platform сравниваются только по matched completed jobs с
   одинаковым quality threshold;
5. labels `EXPERT ESTIMATE` и `CAUSAL ESTIMATE` невозможно перепутать в
   dashboard/demo;
6. residual discovery не создаёт «новый сценарий» из дублей или формулировок
   одного известного use case;
7. passport объясняет membership и рекомендацию без
   доверия к красивому summary;
8. 100k CPU-profile и отсутствие timestamp/run/cost/baseline telemetry не
   ломают demo flow и дают честное `N/A`.

Gate 1 не подтверждает экономический эффект КРОК. Он подтверждает только, что
стратегия корректно ставит вопрос, не допускает двойного счёта и задаёт
проверяемый путь от expert proxy к causal validation.
