# Recovery candidate freeze

Freeze date: 2026-07-24

Branch: `codex/p0-recovery-v2`

Base commit: `356fa282325376e53d9ab1e6968634e7b0ac45f5` (`codex/p0-vertical-slice`)

Frozen candidate commit: `e9ee7a319ac9796809975d70dc902a1906ca1a45`

The frozen candidate is the commit above. This document is a later
documentation-only attestation that references that immutable Git object. No
classifier, parser, taxonomy, threshold, generator, test rubric or label-guide
change is permitted after the candidate commit and before sealed v2 is scored.

## 1. Frozen versions

```text
schema_version: request-event-v2-openai-messages
taxonomy_version: taxonomy-v2-label-guide
algorithm_version: offline-message-aware-v2
external_schema_version: openai-message-challenge-v1
seed: 20260724
abstain_threshold: 0.58
known_match_threshold: 0.48
residual_similarity_threshold: 0.24
near_duplicate_threshold: 0.92
```

## 2. Candidate hashes

```text
candidate_commit_sha:
  e9ee7a319ac9796809975d70dc902a1906ca1a45

git_source_tree_object:
  c4aa6a91482325c5b818d549d776a8f3b2169765

source_sha256:
  9b8fc627146f3b64a5e3d476f2939e50ab3207ec4509259effe26879128cb1ad

config.py_sha256:
  d5e5628b8c0d2f9531f791a448eddfbaa658d510ed24c7fbc6372b80c45d4a09

taxonomy_canonical_sha256:
  6943e970a7f1aa9707301e37ed6792ecfd34dafe2d9e80c46e269d1648aa34c7

label_guide_sha256:
  9903e636df9b299d9d529923985bc13d99dbbc2b4f6dbb9664c62a4825aa27ad

external_gates_canonical_sha256:
  10b2d39e3e59a7f567fbe8c1d2b620d802c152d37b031f95591cd8f70e3ac951

external_manifest_config_sha256:
  c38ca8482d21d8a792127f34365a753e837559d27f5471d30b57a72f4ce53ebc

requirements.txt_sha256:
  c975d615c5987240e1b44280f114a6f110adb266a978b8ebbd8f7e784bfb3a11

pyproject.toml_sha256:
  7c6f1c9acd2c249df73c17eb0f831233c560445ca117fe2539df495b71de7491
```

`source_sha256` is SHA-256 over every sorted `src/prompt_radar/*.py` relative
path, a NUL separator, and its bytes. Taxonomy and gate hashes use canonical
UTF-8 JSON with sorted keys and compact separators.

## 3. Fixed gates

The following thresholds are frozen before any sealed v2 exists.

### External independently labeled challenge

```text
coverage >= 0.50
system macro-F1 >= 0.70
intent macro-F1 >= 0.70
object macro-F1 >= 0.70
```

The CLI reports micro-F1, exact match, Hamming loss, calibration diagnostic and
all axis metrics even when a gate fails. It never changes the model or config.

### Existing Gate-1 controls retained

```text
sealed synthetic macro-F1 >= 0.80
sealed synthetic non-trivial coverage
B-cubed F1 >= 0.75
novelty precision >= 0.70
known-only false emerging == 0
mixed emerging clusters == 0
mean aligned stability >= 0.80 over 10 runs
child-cost reconciliation error == 0
external runtime network calls == 0
security fixture passed
100k suite passed
```

No gate threshold was changed to make sealed v1 or the dummy fixture pass.

## 4. Development sources used

Allowed and used:

- original KROK case PDF and its general task/taxonomy requirements;
- supplied workbook topics A3:A31 and A33 as development source material;
- `context/TELEGRAM_FINDINGS.md`;
- authoritative OpenAI-compatible structure from
  `Структура запроса.txt`;
- authoritative Tatiana Belyakova messages in the Telegram HTML export;
- existing open manual challenge as a development diagnostic only;
- general multi-label invariants recorded in `docs/LABEL_GUIDE.md`;
- synthetic development fixtures:
  `tests/fixtures/openai_messages_dev.json` and
  `tests/fixtures/external_dummy.jsonl`;
- security, economics and long-input regression fixtures.

Explicitly not used for selecting recovery rules, keywords, weights,
thresholds or labels:

- revealed sealed v1 score;
- revealed sealed v1 expected result;
- any future sealed v2 record;
- production KROK logs;
- external API/LLM output.

The sealed v1 texts and labels remain byte-for-byte unchanged from the base
branch. A32 remains an inherited revealed diagnostic, not development data.
`docs/QA_REPORT.md` was not modified.

## 5. Verification at the candidate commit

Clean environment:

```text
Python 3.13.5
duckdb 1.4.3
streamlit 1.54.0
pip install -r requirements.txt: PASS
pip install -e .: PASS
```

Results:

```text
python -m unittest discover -s tests -v
Ran 20 tests
OK

python -m prompt_radar evaluate-external \
  --input tests/fixtures/external_dummy.jsonl ...
records: 1
gate_failures: []
passed: true

python -m prompt_radar run --input <supplied XLSX> ...
exit: 0
run_fingerprint:
  6062d06feea631639a1f36a6ab2ae6ca3fbaa4f3cab09ad1484573116de17952

python -m prompt_radar smoke --input <supplied XLSX> ...
exit: 1
failures: ["sealed-classification-gate"]
```

The last failure is deliberately retained as the historical sealed v1
diagnostic. It was not repaired or used for tuning.

Authoritative Telegram development payload:

```text
message_count: 4
current_goal_chars: 57
system_context_chars: 45
history_user_chars: 63
history_assistant_chars: 4236
retrieval_context_chars: 14903
estimated_total_input_tokens: 2830
context_to_goal_ratio: 282.0
deduplicated_goal_repetitions: 1
redaction_status: passed
```

The extracted current goal was the final `<user_query>`, not the previous
assistant response or RAG topic. Default persisted projection contains no
system/history/assistant/RAG text.

Message-aware regression coverage:

- OpenAI-compatible role parsing and content-parts;
- current goal extraction and duplicate-query removal;
- separate wrapper, retrieval, history, system and tool sections;
- goal at start/middle/end of approximately 100k-word message payload;
- cross-topic RAG does not change goal intent;
- prompt injection remains untrusted data;
- unknown structure quarantines and abstains on every axis;
- seeded PII does not appear in persisted external artifacts.

Artifact security scan found no seeded email, phone or secret canary in the
candidate outputs. The default runtime remained CPU-only and offline.

## 6. External evaluation procedure

After an independent party creates sealed v2, run exactly:

```powershell
python -m prompt_radar evaluate-external `
  --input <opaque.jsonl> `
  --output <new-empty-directory>
```

Record the candidate commit, input SHA-256, produced manifest and exit code.
Do not edit files, rerun with modified config, replace failed output or inspect
individual errors before the result is accepted.

## 7. Declaration

At candidate commit `e9ee7a319ac9796809975d70dc902a1906ca1a45`:

- sealed v2 did not exist and was not created;
- no sealed v2 data was viewed;
- no merge or pull request was performed;
- no LLM, network, GPU or P2/P3 subsystem was added;
- the revealed sealed v1 remained unchanged;
- this recovery candidate was frozen before any external sealed v2 score.
