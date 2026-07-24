# QA report: Prompt Radar P0

Дата проверки: 2026-07-24  
Ветка: `codex/p0-vertical-slice`  
Роль проверки: независимый QA/release review  
Итоговый вердикт: **NO-GO к демо как к прошедшему Gate 1**

## Scope и метод

Проверка выполнена по `prompts/04_qa_release.md`, исходному PDF кейса,
`CASE_CONTEXT.md`, `STAKEHOLDER_INTERVIEW.md`, `DECISION_LOG.md`,
`STRATEGY.md`, `RED_TEAM.md`, `P0_PLAN.md` и `README.md`.

До изменений рабочее дерево было чистым. `main` не изменялся, merge не
выполнялся, продуктовые функции и P0 scope не расширялись.

Чистая среда создана вне репозитория:

```text
Python 3.13.5
pip 25.1.1
duckdb 1.4.3
streamlit 1.54.0
Windows 11; 16 logical CPU
```

Исходная команда README `py -3.12 -m venv .venv` упала с
`No suitable Python runtime found`, несмотря на заявленную совместимость
`Python 3.11+`. После исправления README на `py -3` установка
`requirements.txt` и editable package в новом venv прошла.

## Дефекты и решения

| severity | evidence | impact | fix | verification |
|---|---|---|---|---|
| **BLOCKING, open** | После честного пересчёта sealed synthetic `intent macro-F1 = 0.5000` при gate `>= 0.80`; два E2E smoke завершились `failures: ["sealed-classification-gate"]`, exit code `1`. Причина видна в rubric: общий gold A32 содержит только `create`, хотя одна sealed-формулировка и исходная тема явно содержат `актуализировать`, которое classifier относит к `update`. | Gate 1 не пройден. Менять sealed gold или classifier после просмотра результата означало бы tuning на test и новую утечку. | Не исправлялось в этой версии. Нужны независимая построчная adjudication разметки, новая версия sealed set и повторный запуск только после freeze. | `release-1` и `release-2`: одинаковый fingerprint `d421c9cfb2fa918898e2a81e1037fd278333c95fb7e99ac7529a22bee4dfc100`, одинаковый честный failure. |
| **BLOCKING, open** | В репозитории нет проверяемого provenance независимого разметчика, label guide или adjudication log для `MANUAL_CHALLENGE`; набор и labels находятся рядом с generator/classifier code. | Нельзя независимо подтвердить требование Gate 1 о hand-labeled challenge; хорошие manual scores сами по себе не доказывают независимость. | Не исправлялось: это требует внешней разметки/подтверждения, которого нет в материалах. | Code review `generator.py`; manual и synthetic отчёты остаются разделены. |
| **HIGH, fixed** | Pipeline выбирал паспорт через максимальное пересечение cluster membership с `test_ids`; `grouping_metrics` при `emerging` подменял фактические найденные IDs всем sealed set. Baseline ложно показывал B-cubed/pairwise/ARI/novelty precision `1.0`. | Прямая data leakage и завышенные grouping metrics. | Удалён выбор по split/ground truth. Кандидат выбирается по статусу, stability, support и cohesion. Метрики считаются по фактическим memberships. | Фактическое восстановление `5/6`; B-cubed `0.8387`, pairwise F1 `0.8000`, ARI `0.0000`, novelty precision `1.0000`. Регрессионный тест запрещает возврат к `1.0`. |
| **HIGH, fixed** | Macro-F1 назначал precision/recall `1.0` label-ам без единого expected или predicted случая. Например, отсутствующие intent labels завышали sealed macro-F1 до `0.9000`. | Метрика проходила gate за счёт классов без support. | Macro-F1 теперь считается только по labels с `TP+FP+FN > 0`; список `evaluated_labels` сохраняется в отчёте. | Sealed intent честно упал до `0.5000`; manual key axes остаются выше `0.70`; permutation test проходит. |
| **HIGH, fixed** | Unsupervised residual path создавал ложный `emerging` на known-only dev cluster из записей с abstain по `system`; старый report жёстко писал `known_only_false_emerging = 0`. | Нарушение negative-control gate и ложный use case на экране CTO. | Кластер с неопределёнными `system/business_domain` не допускается в `emerging`; false-emerging считается из реальных candidate clusters. Hard-coded имя, `sealed_challenge` и fictitious distinctness удалены. | `known_only_false_emerging = 0`, `mixed_emerging_clusters = 0`; паспорт grounded: `Email + Project → create + update`. |
| **HIGH, fixed** | Economics итерировала строки runs и могла дважды учесть gross value при повторном `run_id`; duplicate/orphan child events не запрещались. ROI/value-cost ratio не рассчитывались, хотя объявлены контрактом. | Двойной подсчёт business value/cost и неполная проверка формул. | Duplicate `run_id`/`step_id`, ambiguous run IDs и orphan steps теперь отклоняются. Добавлены raw/realized saved time, human-touch cost, run-level и aggregate ROI/value-cost ratio; aggregate ratios считаются из aggregate sums, а не суммой run ratios. | 4 distinct runs, denominator 4, все statuses сохранены, reconciliation error `0`, failed run отрицательный. Unit tests проверяют duplicate rejection и формулы ROI. |
| **HIGH, fixed** | 100k suite выбирала 24/196 chunks (`coverage=0.1224`), но ставила `coverage_warning=false`, если keyword heuristic нашла Email/Project. | Уверенный label при неполном покрытии; риск пропустить цель/противоречие в 88% текста. | При coverage `< 0.15` всегда выставляется warning и явный abstain по system/intent/object; labels этих осей очищаются. | Start/middle/end/injection: без crash/OOM, явный abstain, p95 `0.1798 s`, peak traced RAM `11.41 MB`, injection flag срабатывает. |
| **HIGH, fixed** | Security scan исключал `summary.json` и `dashboard.html`; HTML вставлял evidence без escaping; policy quarantine понимала только `PERSON:`, но не `ФИО:`. | Возможны утечка canary в непроверенные артефакты, stored XSS и публикация явно обозначенного uncertain PII. | Scan охватывает все существующие и prospective artifacts; HTML поля экранируются; `PERSON:`/`ФИО:` с ФИО quarantined. | Seeded email/phone/secret/injection отсутствуют во всех release artifacts; XSS и ФИО regression tests проходят; tracked secret scan нашёл только intentional canary fixtures, key/env файлов нет. |
| **HIGH, fixed** | PowerShell quick start требовал ровно Python 3.12, хотя contract разрешает 3.11+. На QA машине установлен совместимый 3.13, но README-команда падала. | Чистая установка по README невоспроизводима на корректном поддерживаемом Python. | Команда изменена на `py -3 -m venv .venv`. | Новый venv на Python 3.13.5: dependency install, editable install и tests успешны. |

## Проверки после исправлений

### Tests и smoke

```text
python -m unittest discover -s tests -v
Ran 12 tests in 3.451s
OK

python -m compileall -q src tests dashboard
exit 0

python -m prompt_radar smoke ... release-1
exit 1; failures: ["sealed-classification-gate"]

python -m prompt_radar smoke ... release-2
exit 1; failures: ["sealed-classification-gate"]
```

Оба полных прогона включали 100k suite и дали один fingerprint. Статический
`dashboard.html` также имеет одинаковый SHA-256 в обоих прогонах.

Streamlit dashboard загружен через `streamlit.testing.v1.AppTest`: исключений
нет, отрисованы title, passport, три верхние метрики и economics card.

### Честность evaluation и leakage

- A32 отсутствует в dev и known catalog.
- Cross-split exact/near duplicates не найдены при зафиксированном threshold
  `0.92`.
- Выбор cluster/passport больше не получает split/test IDs.
- Sealed grouping: recovered `5/6`, B-cubed `0.8387`, pairwise `0.8000`.
- Sealed classification coverage `1.0000`, но gate честно не пройден:
  `intent macro-F1 = 0.5000`.
- Manual system/intent/object macro-F1:
  `1.0000 / 0.9583 / 0.8889`; independence этой выборки не подтверждена.
- Label permutation по-прежнему обрушивает manual micro-F1 более чем на 0.20.
- Synthetic, manual и sealed synthetic результаты не смешиваются.

### Economics

- Business unit: `distinct(explicit run_id)`, значение `4`.
- Status denominator: `4`; success/partial/failed/cancelled сохранены.
- Gross value: максимум один раз на validated run.
- Child step costs сходятся с run ledger; reconciliation error `0`.
- Формулы:
  `raw saved = B-A-V-W`,
  `realized saved = B*s*q-A-V-W`,
  `gross = B*r*s*q`,
  marginal/fully-loaded cost, net value, ROI и value/cost ratio проверены.
- Failed и cancelled runs дают отрицательный net value.
- Low/base/high выводится только как
  `SYNTHETIC MODEL CHECK / E0 EXPERT ESTIMATE`; action остаётся `VALIDATE`.
- Product comparison 1300/150 users не вычисляется и не заявляется, так как
  он явно вне P0 и для него нет matched pre-outcome cohort.

### Security, offline и artifacts

- Runtime smoke успешно выполнен при monkeypatch, запрещающем
  `socket.socket.connect`; внешних runtime вызовов не потребовалось.
- PII/secret redaction выполняется до persisted analytics.
- Prompt injection заменяется как untrusted data и не меняет configuration.
- Raw adversarial email, phone, secret canary и injection phrase не найдены в
  JSON/JSONL/Parquet/DuckDB/HTML/Markdown artifacts.
- Explicit uncertain person marker приводит к quarantine.
- Default flow не использует LLM, tools, network или raw store для naming.
- Dashboard явно показывает `SYNTHETIC DEMO`, sealed challenge, `E0` и
  offline CPU; dynamics/failure telemetry обозначены `N/A`.

## Неблокирующие ограничения

- Peak RAM отражает только Python `tracemalloc` для sketch path, а не полный
  process RSS. Для production capacity planning этого недостаточно.
- Contract громко отклоняет XLSX с пустой строкой в A3:A33, но отдельного
  универсального within-split near-dedup stage нет. На поставленном workbook
  exact empty/duplicate contract failure не воспроизведён.
- Calibration реализована как средняя абсолютная ошибка по пяти осям, а не
  полноценные reliability bins; для P0 это диагностическая, не causal метрика.

## Финальный release verdict

**NO-GO.**

Runtime, offline fallback, security, 100k path, run accounting, grouping и
воспроизводимость после исправлений технически работают. Но выпуск нельзя
называть прошедшим Gate 1: честный sealed classification gate падает, а
независимость manual challenge не доказана. Исправлять это подгонкой текущего
classifier/gold после просмотра test запрещено. Следующий допустимый шаг -
внешняя построчная adjudication, новый versioned sealed challenge, freeze
taxonomy/rubric/thresholds и один новый test run.
