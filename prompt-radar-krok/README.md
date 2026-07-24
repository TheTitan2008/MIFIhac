# Prompt Radar — offline Gate-1 vertical slice

Рабочий CPU-only прототип Evidence-First Opportunity Radar для кейса КРОК.
Один batch-проход читает исходный XLSX с 31 темой, создаёт строго
маркированный synthetic dataset, классифицирует запросы, отделяет known от
residual, строит один sealed-challenge evidence passport, сверяет run-level
economics и формирует локальный dashboard.

> Все demo-данные и экономика синтетические. `E0` означает экспертную оценку,
> а не доказанный ROI КРОК. Внешних API и LLM в runtime нет.

## Что входит

- фиксированный contract и split до augmentation;
- `A32` и производные только в sealed test, не в dev/catalog/tuning;
- PII/secret redaction до vector/cache/persistence и quarantine path;
- deterministic multi-axis classifier с confidence/abstention;
- known matcher и constrained residual discovery;
- десять aligned perturbation runs и known-only negative control;
- extractive passport `Email → Project`;
- один `agent_run` как business unit, child-cost reconciliation и
  low/base/high `E0` sensitivity;
- отдельные synthetic и independently hand-labeled metrics;
- expected labels зафиксированы отдельным source-row rubric и не вычисляются
  тестируемым classifier; permutation test обрушает score;
- обязательные 100k-token start/middle/end/injection smoke cases;
- DuckDB + Parquet artifacts, статический HTML и Streamlit dashboard.

Не входят: product comparison, causal estimate, GPU, внешняя/локальная LLM,
real-time, MLOps и P2/P3-полировка.

## Быстрый запуск

Требуется Python 3.11+.

PowerShell:

```powershell
cd C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .

$xlsx = 'C:\Users\aleks\Downloads\Темы для генерации датасета.xlsx'
.\.venv\Scripts\python.exe -m prompt_radar run `
  --input $xlsx `
  --output artifacts\latest
```

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e .
.venv/bin/python -m prompt_radar run \
  --input "/path/to/Темы для генерации датасета.xlsx" \
  --output artifacts/latest
```

Команда `run` формирует offline artifacts и завершается кодом `0`.
Команда `smoke` сохраняет раскрытый sealed v1 как исторический diagnostic; его
честный `sealed-classification-gate` не исправляется и не используется для
tuning recovery candidate.

## OpenAI-compatible messages

Recovery adapter принимает payload с `model`, `stream` и `messages`. Он
разделяет последний current user goal, task wrapper, RAG context, историю
user/assistant, system/developer и tool messages. Классификация выполняется по
current goal; длинный контекст не подменяет intent.

В default persisted projection сохраняются redacted goal, размеры секций,
token estimates, context/goal ratio и технические flags. Полные system,
assistant и RAG тексты не сохраняются.

Правила разметки: `docs/LABEL_GUIDE.md`.

## External opaque evaluation

После freeze внешний challenge запускается без обновления classifier,
taxonomy, thresholds или guide:

```powershell
.\.venv\Scripts\python.exe -m prompt_radar evaluate-external `
  --input challenge.jsonl `
  --output artifacts\external
```

Одна строка JSONL:

```json
{
  "request_id": "opaque-001",
  "payload": {
    "model": "openai-compatible-model",
    "stream": true,
    "messages": [
      {"role": "user", "content": "Найди документ в Confluence"}
    ]
  },
  "expected_labels": {
    "system": ["Confluence"],
    "intent": ["search"],
    "object": ["document"],
    "automation_mode": ["one_shot"],
    "business_domain": ["knowledge"]
  }
}
```

Интерфейс пишет `evaluation.json`, frozen `manifest.json` и безопасный
`parsed_requests.jsonl`. Он только измеряет заранее определённые метрики и не
выполняет fit/tuning.

## Dashboard

Статический результат smoke доступен в `artifacts/latest/dashboard.html`.
Интерактивный локальный dashboard:

```powershell
$env:PROMPT_RADAR_OUTPUT = 'artifacts\latest'
.\.venv\Scripts\streamlit.exe run dashboard\app.py
```

Streamlit читает только уже сформированные локальные artifacts. Сеть,
H100 и secrets не нужны.

## Тесты

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Тесты покрывают XLSX contract, ручную challenge-выборку, PII/injection,
run-cost reconciliation, long-input sketch и запись DuckDB/Parquet/dashboard.

## Артефакты одного run

- `summary.json` — итог Gate и честные labels;
- `manifest.json` — input/config/source hashes и deterministic fingerprint;
- `evaluation.json` — synthetic/manual/grouping/leakage отчёты;
- `evaluation.md` — человекочитаемый evaluation report;
- `passport.json` — один evidence passport;
- `economics.json` — reconciled `E0` model check;
- `long_input.json` — 100k latency/RAM/start-middle-end-injection suite;
- `prompt_radar.duckdb` и `*.parquet` — redacted аналитические таблицы;
- `dashboard.html` — статический executive report.
- `history/<run_fingerprint>.json` — immutable snapshot повторного test run.

Raw instruction text не сохраняется в default artifacts. Таблица
`request_event` содержит только redacted text.

## Воспроизводимость

Seed, schema, taxonomy и algorithm versions фиксированы. Manifest хэширует
входной XLSX и Python source. Два запуска неизменного кода/входа дают одинаковый
`run_fingerprint`; измеренная latency не входит в deterministic fingerprint.

Архитектурные границы и принятые решения: `docs/P0_PLAN.md`,
`docs/STRATEGY.md`, `docs/RED_TEAM.md`, `context/DECISION_LOG.md`.
