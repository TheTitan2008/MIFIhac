from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st


artifact_dir = Path(os.environ.get("PROMPT_RADAR_OUTPUT", "artifacts/latest"))
summary_path = artifact_dir / "summary.json"

st.set_page_config(page_title="Prompt Radar", layout="wide")
st.title("Prompt Radar — Evidence-First Opportunity Radar")

if not summary_path.exists():
    st.error(f"Сначала запустите batch pipeline: не найден {summary_path}")
    st.stop()

summary = json.loads(summary_path.read_text(encoding="utf-8"))
passport = summary["passport"]
economics = summary["economics"]
evaluation = summary["evaluation"]

st.warning("SYNTHETIC DEMO · SYNTHETIC SEALED CHALLENGE · EXPERT ESTIMATE (E0)")
st.caption("Offline CPU batch. Не является доказательством ROI или реальным инсайтом КРОК.")

left, middle, right = st.columns(3)
left.metric("Независимые формулировки", passport["support_canonical_groups"])
middle.metric("Aligned stability", passport["stability"]["mean_jaccard"])
right.metric("Business tasks", economics["business_task_count"])

st.header(passport["name"])
st.write(passport["summary"])
st.write(
    {
        "status": passport["status"],
        "action": passport["action"],
        "naming_method": passport["naming_method"],
        "cohesion": passport["cohesion"],
        "distinctness": passport["distinctness"],
    }
)
with st.expander("Redacted evidence", expanded=True):
    for example in passport["examples"]:
        st.code(example)
st.info(passport["dynamics"])
st.info(passport["failure_signal"])

st.header("Ценность против стоимости")
scenario = st.radio("Sensitivity", ["low", "base", "high"], horizontal=True, index=1)
totals = economics["scenarios"][scenario]["totals"]
e1, e2, e3 = st.columns(3)
e1.metric("Gross value (model check)", round(totals.get("gross_value", 0), 2))
e2.metric("Marginal cost", round(totals.get("marginal_cost", 0), 2))
e3.metric("Fully-loaded cost", round(totals.get("fully_loaded_cost", 0), 2))
st.error(f"{economics['label']} · action={economics['action']}")

st.header("Evaluation")
st.json(
    {
        "synthetic": evaluation["synthetic"],
        "manual": evaluation["manual"],
        "grouping": evaluation["grouping"],
        "leakage": evaluation["leakage"],
    },
    expanded=False,
)
st.caption(f"Run fingerprint: {summary['manifest']['run_fingerprint']}")
