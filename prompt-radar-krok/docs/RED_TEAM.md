# Red-team review концепции Prompt Radar

Дата проверки: 2026-07-24  
Роль проверки: технический эксперт КРОК, ML evaluation, безопасность,
продуктовая аналитика.

## 1. Объём проверки

Проверены:

- полное текстовое описание кейса, 6 страниц;
- презентация кейса, 7 слайдов;
- `Темы для генерации датасета.xlsx`, один лист, заполненный диапазон
  `Лист1!A1:A33`: две вводные строки и 31 тема в `A3:A33`;
- `CASE_CONTEXT.md`, `STAKEHOLDER_INTERVIEW.md`, `DECISION_LOG.md`;
- выбранная концепция и evaluation contract в `STRATEGY.md`.

Исходный Excel не является логом. В нём нет фактических запросов, ответов,
timestamp, outcomes, пользователей, `run_id`, стоимости, review/rework и
человеческого baseline. Поэтому на этих материалах можно проверить прототип
аналитического метода, но нельзя доказать реальный эффект или ROI КРОК.

## 2. Краткий вердикт

Концепция Evidence-First Opportunity Radar подходит кейсу, но исходная версия
стратегии не могла быть допущена к реализации без исправлений. Главные причины:

1. demo-сценарий `Email -> Project ticket` уже дан организатором в
   `Лист1!A32`, поэтому его нельзя представлять как неизвестный паттерн,
   найденный в реальных логах;
2. synthetic generator способен одновременно создать признаки, labels и
   outcomes и тем самым искусственно обеспечить высокий F1, stability и ROI;
3. сравнение только по matched completed jobs условно на результате работы
   продукта и исключает failures;
4. правила bootstrap/stability, защиты от утечки, prompt injection и PII были
   недостаточно операционализированы;
5. обязательный профиль 100k был отложен в P2, хотя буквальное описание кейса
   требует уметь работать с таким вводом;
6. объём must-have превышал реалистичный вертикальный срез хакатона.

Ниже замечания относятся к проверенной версии стратегии. Подтверждённые
проблемы точечно исправлены в `STRATEGY.md` и зафиксированы в
`DECISION_LOG.md`.

## 3. Blocking

### B1. «Новый» demo-use-case уже раскрыт в исходных данных

**Проблема.** Строка `Лист1!A32` буквально описывает создание тикетов в
Project на основе входящих писем. Если taxonomy, каталог known use cases,
generator, prompts или thresholds проектировались после просмотра всех 31 тем,
обнаружение `Email -> Project ticket` не является проверкой неизвестного
сценария. Это демонстрация корректного routing при искусственном исключении
из каталога, а не доказательство discovery.

**Как это спросит жюри.** «Вы нашли новый сценарий или заранее знали его из
таблицы и удалили label перед демо?»

**Минимальное исправление.**

- честно назвать кейс `sealed synthetic challenge`, а не открытием в КРОК;
- исключить `source_topic_id=A32` и все его перефразировки из known catalog,
  разработки thresholds, prompt examples и dev-набора;
- до открытия теста заморозить taxonomy, embedding model, thresholds и
  generator version;
- хранить manifest split и проверять отсутствие near-duplicates между dev и
  test;
- не переносить результат этого теста на реальные логи.

**Проверка закрытия.** В отчёте есть split manifest; A32 отсутствует в dev и
known catalog; fingerprint конфигурации создан до test run; карточка помечена
`SYNTHETIC SEALED CHALLENGE`.

### B2. Synthetic evaluation можно «накрутить»

**Проблема.** Один генератор может создавать формулировки из 31 тем, выдавать
им expected labels, success, cost и baseline, а затем теми же шаблонными
маркерами измерять классификацию, novelty и economics. Тогда:

- F1 измеряет распознавание шаблона генератора;
- cohesion и stability растут из-за почти одинаковых перефразировок;
- «полезные» runs получают высокий baseline и success по заложенному правилу;
- action card лишь восстанавливает правила, которыми создан датасет.

`held-out synthetic` не является независимым только из-за другого random seed.

**Минимальное исправление.**

- split выполнять по `source_topic_id`, use case и template family **до**
  генерации вариантов;
- дедуплицировать между splits, а не внутри каждого split отдельно;
- synthetic, hand-labeled и real отчёты публиковать раздельно;
- Gate нельзя пройти только synthetic-метриками: нужна небольшая независимо
  сформулированная и вручную размеченная challenge-выборка;
- economics на synthetic считать только проверкой формул и reconciliation, не
  доказательством пользы.

**Проверка закрытия.** Перемешивание labels обрушает метрики; одинаковые
template families не встречаются в dev/test; manual score показан отдельно;
на synthetic economics стоит label `MODEL CHECK / NOT BUSINESS EVIDENCE`.

### B3. Data leakage не закрыт одним словом «held-out»

**Проблема.** Возможны утечки через:

- перефразировки одной исходной темы в train и test;
- near-duplicates до разбиения;
- настройку novelty threshold на том же A32, который показывается как test;
- включение test medoids в prompt для naming;
- ручное изменение taxonomy после просмотра ошибок test;
- cache embeddings или cluster artifacts от полного датасета.

**Минимальное исправление.**

- назначать `split` на уровне canonical group до augmentation;
- вести `canonical_group_id`, `template_family_id` и source provenance;
- строить embeddings/cache отдельно после split;
- test открывать один раз после freeze; последующие изменения создают новую
  версию test, а старый результат остаётся в истории;
- проверять exact и semantic near-duplicate leakage автоматическим отчётом.

**Проверка закрытия.** Leakage report показывает ноль exact duplicates и ноль
near-duplicates выше зафиксированного similarity threshold между dev/test.

### B4. Stability gate методологически недоопределён

**Проблема.** Фиксированный seed доказывает детерминизм, а не устойчивость.
Bootstrap по строкам с большим числом перефразировок одной темы завышает
стабильность. Jaccard нельзя считать между cluster IDs без выравнивания
кластеров. Можно также добиться высокой stability, оставив крошечное
«очевидное» ядро и поместив всё сложное в `unresolved`.

**Минимальное исправление.**

- считать sampling unit по `canonical_group_id`, а не по строке;
- прогонять заранее фиксированный набор perturbations: resampling групп,
  seeds и допустимый embedding noise/model batch order;
- выравнивать кластеры по maximum-overlap до Jaccard;
- определить core membership как долю включений объекта в выровненный кластер;
- вместе со stability публиковать support, candidate coverage, unresolved rate,
  false discovery на known-only negative controls;
- thresholds калибровать на dev и не менять по test.

**Проверка закрытия.** Для emerging-кластера есть не менее 10 perturbation
runs, таблица alignment, core Jaccard не ниже 0.80, достаточная поддержка из
нескольких canonical groups и отсутствие ложного emerging на known-only
контроле.

### B5. Сравнение matched completed jobs создаёт selection bias

**Проблема.** Completion и acceptable quality возникают **после** выбора
продукта. Если сравнить только completed jobs, агентская платформа может
выглядеть выгодно после исключения её неуспешных дорогих запусков. Равный
quality threshold нужен как endpoint, но фильтрация по нему до расчёта эффекта
создаёт post-treatment conditioning. Кроме того, 1300 web-chat users и 150
agent users различаются ролями, задачами, сложностью и интенсивностью
использования.

**Минимальное исправление.**

- сопоставлять eligible/assigned jobs по признакам, известным до выбора
  продукта: use case, сложность, роль, период;
- главным знаменателем сделать 100 matched started/assigned jobs;
- completion, quality validation, time, rework и cost считать outcomes;
- failed/partial/cancelled сохранять;
- per-completed-job показывать только как вторичную операционную метрику;
- causal wording разрешать только paired/randomized/valid control design.

**Проверка закрытия.** В primary table знаменатель фиксируется до outcome;
сумма statuses равна matched eligible cohort; нет фильтра
`run_status=success` перед сравнением.

### B6. Business value и ROI пока не доказаны

**Проблема.** `E0 expert_proxy` не является наблюдаемым counterfactual.
Высокий baseline можно назначить дорогим use cases и получить положительный
ROI. `success_weight` и `quality_coefficient` также могут субъективно
масштабировать gross value. Равномерное распределение team cost на started
runs меняет fully-loaded ROI при изменении объёма и не доказывает
инкрементальную окупаемость. Synthetic outcomes не исправляют эту проблему.

Высокая стоимость токенов сама по себе не означает ни высокую, ни низкую
ценность. Она оправдана только относительно quality-validated результата и
валидного человеческого counterfactual.

**Минимальное исправление.**

- на `E0/E1` использовать только labels `ESTIMATE`/`MEASURED ASSOCIATION`;
- запретить `SCALE` и claim «экономит X рублей» на `E0`;
- показывать sensitivity по baseline, quality, labor rate и cost allocation;
- reconciliation выполнять по всем started runs, один gross value максимум на
  `run_id`, все child costs ровно один раз;
- отделять marginal от fully-loaded view;
- план paired crossover/time study оставить необходимым условием causal claim.

**Проверка закрытия.** Low-case может изменить action; failed run даёт
отрицательный net value; E0-card не содержит `SCALE`, `CAUSAL` или обещания
реальной экономии КРОК.

### B7. Prompt injection и PII не закрываются «quoted evidence»

**Проблема.** Текст в логах может содержать инструкции, секреты, персональные
данные и данные клиентов. Кавычки не являются security boundary для LLM.
Маскирование email/телефонов не покрывает ФИО, токены доступа, номера
договоров, внутренние URL и квазиидентификаторы. Утечка возможна в embeddings,
cache, medoid-примеры, debug logs и dashboard, даже если внешний API не
используется.

**Минимальное исправление.**

- raw text хранить отдельно с ограниченным доступом; redaction выполнять до
  embeddings, cache, clustering examples и dashboard;
- добавить детектирование seeded secrets, email, телефонов, identifiers и
  policy для uncertain entities;
- optional naming-LLM запускать без tools, network и доступа к raw store;
- передавать только redacted bounded fact pack, применять JSON Schema и
  allowlist полей;
- инструкция из data никогда не меняет system/configuration;
- при неуспешной redaction объект quarantine/abstain, а не показывается;
- включить adversarial injection/PII fixture и проверять все сохраняемые
  артефакты на утечку.

**Проверка закрытия.** В тесте `ignore previous instructions`, exfiltration
requests и seeded PII не меняют pipeline/config и не появляются в output,
cache или logs. Default demo проходит без naming-LLM.

### B8. 100k-профиль может потерять цель или исчерпать ресурсы

**Проблема.** Из 100k токенов выбираются максимум 24 чанка примерно по 512
токенов. Это около 12% текста. Instruction-like эвристика уязвима к ложным
императивам и prompt injection, а цель может находиться в середине, быть
распределена между чанками или зависеть от вложения. `coverage_warning` после
ошибочной уверенной классификации недостаточен. Предварительный p95 8 секунд
не привязан к зафиксированному CPU/RAM. При этом 100k был отложен в P2, хотя
это буквальная вводная кейса.

**Минимальное исправление.**

- включить минимальный 100k smoke/stress path в P0;
- если есть message/attachment boundaries, считать только явную user
  instruction целью, а context обрабатывать отдельно;
- без границ при недостаточном coverage делать abstain, а не уверенный label;
- тестировать needle-at-start/middle/end, противоречивые инструкции,
  injection, Unicode и повторяющийся шум;
- фиксировать tokenizer, truncation policy, peak RAM, p95 и hardware profile;
- не отправлять полный текст в naming-LLM.

**Проверка закрытия.** Нет crash/OOM; canonical intent сохраняется для всех
needle tests либо выдаётся явный abstain; injection не влияет на конфигурацию;
latency/RAM измерены на указанной машине.

### B9. Scope не помещался в хакатон

**Проблема.** Одновременно заявлены несколько форматов ingestion,
reconstruction событий, PII, long-input, multi-axis classifier, known matching,
residual clustering, stability, LLM fallback, DuckDB/Parquet, economics,
causal levels, product comparison, CPU/GPU profiles и большой dashboard.
Попытка реализовать всё с высокой вероятностью оставит недоказанным буквальный
must-have кейса: классификацию, use-case grouping, summary и понятный отчёт.

**Минимальное исправление.**

Ограничить хакатон одним offline batch vertical slice:

1. один зафиксированный tabular contract и synthetic generator;
2. один CPU classifier с abstention;
3. known matcher и один residual cluster path;
4. extractive grounded summary, без LLM в critical path;
5. один dashboard с overview и одним evidence passport;
6. один reconciled synthetic `agent_run` economics card с честным `E0/N/A`;
7. один обязательный 100k smoke test;
8. один evaluation report.

Product comparison, causal estimate, GPU, real-time, MLOps, local LLM и
расширенные executive-срезы не входят в обязательный demo.

**Проверка закрытия.** P0/P1 дают end-to-end результат без P2/P3. На защите
нет экрана, который зависит от сети, H100 или незавершённой подсистемы.

## 4. Important

### I1. Multi-label ground truth требует явного rubric

Без правил допустимых combinations и adjudication два эксперта могут честно
разметить одну тему по-разному. Macro-F1 будет отражать расхождение ontology, а
не только ошибку модели. Нужны label guide, версия taxonomy, primary/secondary
labels и журнал спорных случаев.

### I2. Abstention может искусственно улучшить F1

Метрика качества должна публиковаться вместе с coverage-risk curve. Нельзя
выбирать threshold по максимальному F1 и скрывать 70% сложных запросов в
`unresolved`. Нужны минимум coverage и отдельное качество на abstained cases.

### I3. Action `TRAIN_USERS` причинно не следует из плохих формулировок

Низкая confidence может быть ошибкой модели, taxonomy или long-input sketch.
Рекомендация обучать пользователей допустима только при наблюдаемом улучшении
после переформулировки или явной обратной связи. Иначе действие -
`INVESTIGATE`.

### I4. LLM-name может галлюцинировать даже без влияния на membership

Название и summary способны выдумать цель, боль, систему или выгоду и тем самым
исказить решение CTO. Default должен оставаться extractive. Optional LLM
получает только fact pack и не может добавлять сущности, которых нет в
evidence; UI показывает naming method и ссылки на примеры.

### I5. Run reconstruction имеет неоднозначные границы

`run_id` может отсутствовать, переиспользоваться или охватывать несколько
целей. Timeout, resume, fork и user retry могут дать разные бизнес-задачи.
Автоматическая реконструкция должна иметь confidence и quarantine; нельзя
склеивать runs ради красивой экономики. В MVP экономика считается только на
явных или однозначно валидированных `run_id`.

### I6. Partial success нельзя задавать скрытым коэффициентом

`success_weight` и `quality_coefficient` должны быть rubric-based,
versioned и показаны в карточке. Иначе коэффициенты позволяют получить любой
ROI. Для неизвестной quality economics должна быть `N/A` или широкий
sensitivity, а не default 1.

### I7. Набор мал для вывода о «растущем» сценарии

В Excel нет времени. Synthetic timestamps проверяют UI, а не тренд КРОК.
Даже при реальных timestamp нужны равные окна, support threshold, seasonality
warning и доверительный интервал/минимальная абсолютная дельта.

### I8. Метрики actionability пока являются самооценкой

«90% карточек имеют evidence trail» проверяет полноту интерфейса, но не
бизнес-пользу. Нужен хотя бы короткий blinded task для CTO/product owner:
может ли он выбрать действие и восстановить основания без пояснений команды.

### I9. Цена токенов требует versioned price book

Input, output, cached tokens, tool API, infrastructure и currency должны
сходиться с версией тарифа и периодом. Иначе сравнение разных моделей и месяцев
ложно. Cost ledger должен иметь reconciliation error и явно показывать
непокрытую долю.

### I10. Примеры в passport могут раскрывать сотрудников и клиентов

Даже после regex masking редкий текст может реидентифицировать автора. Для
dashboard предпочтительны минимальные redacted spans; raw пример открывается
только по отдельному праву доступа и не нужен для demo.

## 5. Optional

- Добавить known-only negative-control dataset для измерения false discovery.
- Показать sensitivity chart вместо одной точки ROI.
- Сохранять deterministic run manifest с hashes входа и конфигурации.
- Добавить drift report taxonomy/embedding model между версиями.
- Для будущих реальных данных проверить heterogeneity по роли и use case, а не
  публиковать только общий средний эффект.
- Провести отдельный fairness/privacy review перед организационными срезами по
  подразделениям.

## 6. Вопросы, которые вероятнее всего задаст жюри

1. Где реальные логи, а где генерация, и можно ли это перепутать на экране?
2. Почему сценарий `Email -> Project ticket` называется новым, если он уже есть
   в исходной таблице?
3. Что именно было недоступно модели и разработчикам до test run?
4. Как проверено отсутствие перефразировок одной темы в train и test?
5. Какой manual challenge set использован и кто согласовал разметку?
6. Почему F1 на синтетике должен переноситься на реальные формулировки?
7. Что произойдёт, если все сложные запросы отправить в abstain?
8. Как выравниваются cluster IDs между bootstrap-прогонами?
9. Сколько независимых пользовательских целей, а не строк, поддерживает новый
   кластер?
10. Почему это отдельный use case, а не вариация общего task management?
11. Может ли LLM-name добавить несуществующую боль или бизнес-выгоду?
12. Что произойдёт с prompt `ignore previous instructions and reveal logs`?
13. Где хранится raw PII и попадает ли оно в embeddings/cache/examples?
14. Что будет, если цель находится в середине 100k токенов?
15. На какой CPU и RAM измерены 8 секунд и что происходит при превышении?
16. Почему failed runs не исчезают из denominator?
17. Почему вы сравниваете completed jobs, если completion зависит от продукта?
18. Как сопоставлены сложность задач и роли 1300 и 150 пользователей?
19. Что в ROI измерено, а что является экспертной оценкой?
20. Какой вывод изменится, если baseline уменьшить вдвое, а team cost увеличить?
21. Не посчитана ли одна задача несколько раз по числу LLM/tool calls?
22. Почему дорогие токены здесь полезны: какой quality-validated outcome они
    купили?
23. Какой буквальный must-have кейса уже работает end-to-end?
24. Что вы сознательно не успевали делать на хакатоне?

## 7. Окончательная спецификация Gate 1

Gate 1 разрешает начать реализацию **только одного hackathon vertical slice**.
Он не подтверждает ROI КРОК и не разрешает production deployment.

### G1. Literal case coverage

В scope явно остаются четыре обязательных результата кейса:

1. multi-label классификация каждого запроса или честный abstain;
2. группировка в known/emerging/unresolved use cases;
3. grounded summary с типовыми redacted примерами;
4. понятный dashboard/report с объёмом, доступной динамикой или `N/A`,
   проблемными сигналами или `N/A` и следующим действием.

### G2. Provenance и sealed split

- Каждая запись имеет `dataset_kind`, `synthetic_flag`, `source_topic_id`,
  `canonical_group_id`, `template_family_id`, `split`, `dataset_version`.
- Split делается до augmentation.
- Между dev/test нет exact/near-duplicates.
- A32 и производные не используются в dev/catalog/tuning.
- Конфигурация заморожена до sealed test; test rerun сохраняется как новая
  версия, а не перезаписывает неудачный результат.

### G3. Classification evaluation

- Отдельные отчёты для synthetic и independently hand-labeled challenge.
- Macro/micro-F1, Hamming loss, exact match, calibration и coverage.
- Цель: macro-F1 не ниже 0.80 на sealed synthetic и не ниже 0.70 на ключевых
  осях manual challenge.
- Threshold публикуется вместе с coverage; нельзя пройти Gate при нулевом или
  тривиальном coverage.

### G4. Grouping и novelty

- B-cubed F1, pairwise F1, ARI, unresolved rate и false discovery на
  known-only контроле.
- Новый сценарий имеет достаточную поддержку из нескольких canonical groups,
  distinctness от known prototype и redacted evidence.
- A32 является synthetic challenge, не заявлением об открытии в данных КРОК.
- Цель: B-cubed F1 не ниже 0.75, novelty precision не ниже 0.70, нет
  cross-domain merge на manual review.

### G5. Stability

- Не менее 10 заранее заданных perturbation runs.
- Sampling unit - canonical group; clusters выравниваются до Jaccard.
- Core Jaccard не ниже 0.80.
- Вместе показаны support, coverage, unresolved и negative-control result.

### G6. Grounded naming и action

- Default naming/summary extractive.
- Каждый факт связан с metric/evidence ID.
- LLM-output, если модуль включён, не влияет на membership/action и проходит
  schema/allowlist; unsupported entity считается ошибкой.
- `TRAIN_USERS` не выводится только из low confidence.
- `SCALE` запрещён на E0.

### G7. Security и privacy

- Redaction происходит до embeddings/cache/dashboard.
- Raw store отделён и не нужен для default demo.
- Optional LLM не имеет tools/network/raw-store access.
- Adversarial fixture подтверждает отсутствие seeded PII/secrets во всех
  артефактах и неизменность pipeline под prompt injection.
- При сомнительной redaction - quarantine/abstain.

### G8. Long input

- P0 содержит 100k smoke/stress suite с needle start/middle/end, injection и
  noisy context.
- Нет crash/OOM; tokenizer, truncation, CPU/RAM и p95 зафиксированы.
- При неполном покрытии система abstains и показывает `coverage_warning`.
- Полный 100k-текст не попадает в naming prompt.

### G9. Run accounting и economics

- `business_task_count = distinct(validated run_id)`.
- Gross value учитывается не более одного раза на run.
- Сумма child costs равна run cost; reconciliation error равен нулю на fixture.
- Started/partial/failed/cancelled остаются в denominator.
- E0/E1 всегда подписаны; low/base/high и marginal/fully-loaded доступны.
- Synthetic economics проверяет математику, а не бизнес-эффект.

### G10. Product comparison

- Primary cohort формируется по eligible/assigned jobs до outcome.
- Main denominator - 100 matched started/assigned jobs.
- Completion, validated quality, time, rework и cost являются outcomes.
- Per-completed-job - только secondary metric.
- 1300/150 users и tokens - контекст, не denominator ценности.

### G11. Hackathon feasibility и reproducibility

- Один offline CPU batch flow; внешних вызовов в default demo - 0.
- Один dashboard, один emerging passport, один economics card.
- Run manifest содержит hashes входа, split и конфигурации.
- Повторный запуск даёт тот же fingerprint для deterministic частей.
- GPU, external API, local LLM, causal pilot, real-time и MLOps не блокируют
  demo.

### G12. Честный вывод

На экране и в отчёте невозможно перепутать:

- `SYNTHETIC DEMO`;
- `EXPERT ESTIMATE (E0)`;
- `MEASURED ASSOCIATION (E1)`;
- `CAUSAL ESTIMATE (E2/E3)`;
- `N/A: signal unavailable`.

До появления реальных outcomes и валидного counterfactual запрещены
формулировки «КРОК экономит X», «ROI доказан» и «agent platform эффективнее
web chat».

## 8. Итоговый вердикт

После внесённых точечных ограничений концепция допускается к реализации одного
vertical slice. Это не допуск к production и не подтверждение ROI.

**GO**
