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
.\.venv\Scripts\python.exe -m prompt_radar smoke `
  --input $xlsx `
  --output artifacts\latest
```

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e .
.venv/bin/python -m prompt_radar smoke \
  --input "/path/to/Темы для генерации датасета.xlsx" \
  --output artifacts/latest
```

Успешный smoke завершается кодом `0` и печатает `failures: []`.

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
