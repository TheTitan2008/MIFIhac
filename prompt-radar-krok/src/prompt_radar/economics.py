from __future__ import annotations

from collections import Counter


def synthetic_run_fixture() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    statuses = ["success", "partial", "failed", "cancelled"]
    runs = []
    steps = []
    for index, status in enumerate(statuses, start=1):
        run_id = f"econ-run-{index}"
        success_weight = {"success": 1.0, "partial": 0.5, "failed": 0.0, "cancelled": 0.0}[status]
        quality = {"success": 0.95, "partial": 0.6, "failed": 0.0, "cancelled": 0.0}[status]
        child_costs = [0.18 + index * 0.01, 0.07, 0.05]
        for step_index, cost in enumerate(child_costs, start=1):
            steps.append(
                {
                    "step_id": f"{run_id}-step-{step_index}",
                    "run_id": run_id,
                    "step_type": "llm" if step_index < 3 else "tool",
                    "cost": round(cost, 4),
                }
            )
        runs.append(
            {
                "run_id": run_id,
                "run_id_validation": "explicit",
                "run_status": status,
                "success_weight": success_weight,
                "quality_score": quality,
                "baseline_low_minutes": 20.0,
                "baseline_base_minutes": 35.0,
                "baseline_high_minutes": 50.0,
                "labor_cost_per_minute": 1.2,
                "user_active_minutes": 2.0,
                "human_review_minutes": 3.0 if status == "success" else 6.0,
                "rework_minutes": 0.0 if status == "success" else 8.0,
                "child_cost": round(sum(child_costs), 4),
                "infrastructure_cost": 0.08,
                "team_allocation_cost": 0.25,
                "synthetic_flag": True,
                "evidence_level": "E0",
            }
        )
    return runs, steps


def calculate_economics(
    runs: list[dict[str, object]], steps: list[dict[str, object]]
) -> dict[str, object]:
    run_ids = [str(run["run_id"]) for run in runs]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("Duplicate run_id would double-count business value")
    if any(run.get("run_id_validation") != "explicit" for run in runs):
        raise ValueError("Economics requires explicit validated run_id")
    step_ids = [str(step["step_id"]) for step in steps]
    if len(step_ids) != len(set(step_ids)):
        raise ValueError("Duplicate step_id would double-count child cost")
    orphan_run_ids = {str(step["run_id"]) for step in steps} - set(run_ids)
    if orphan_run_ids:
        raise ValueError(f"Orphan child costs for run_id: {sorted(orphan_run_ids)}")

    step_cost: Counter[str] = Counter()
    for step in steps:
        step_cost[str(step["run_id"])] += float(step["cost"])
    scenarios = {}
    for scenario in ("low", "base", "high"):
        totals = Counter()
        rows = []
        for run in runs:
            run_id = str(run["run_id"])
            baseline = float(run[f"baseline_{scenario}_minutes"])
            success = float(run["success_weight"])
            quality = float(run["quality_score"])
            labor = float(run["labor_cost_per_minute"])
            touch_minutes = sum(
                float(run[key])
                for key in ("user_active_minutes", "human_review_minutes", "rework_minutes")
            )
            gross = baseline * labor * success * quality
            human_touch = touch_minutes * labor
            marginal = step_cost[run_id] + float(run["infrastructure_cost"]) + human_touch
            fully_loaded = marginal + float(run["team_allocation_cost"])
            row = {
                "run_id": run_id,
                "gross_value": round(gross, 4),
                "child_step_cost": round(step_cost[run_id], 4),
                "human_touch_cost": round(human_touch, 4),
                "marginal_cost": round(marginal, 4),
                "fully_loaded_cost": round(fully_loaded, 4),
                "net_value_marginal": round(gross - marginal, 4),
                "net_value_fully_loaded": round(gross - fully_loaded, 4),
                "raw_net_saved_minutes": round(baseline - touch_minutes, 4),
                "realized_net_saved_minutes": round(
                    baseline * success * quality - touch_minutes, 4
                ),
                "roi_marginal": round((gross - marginal) / marginal, 4)
                if marginal
                else None,
                "roi_fully_loaded": round((gross - fully_loaded) / fully_loaded, 4)
                if fully_loaded
                else None,
                "value_cost_ratio_marginal": round(gross / marginal, 4)
                if marginal
                else None,
                "value_cost_ratio_fully_loaded": round(gross / fully_loaded, 4)
                if fully_loaded
                else None,
            }
            rows.append(row)
            totals.update(
                {
                    key: value
                    for key, value in row.items()
                    if key
                    not in {
                        "run_id",
                        "roi_marginal",
                        "roi_fully_loaded",
                        "value_cost_ratio_marginal",
                        "value_cost_ratio_fully_loaded",
                    }
                }
            )
        total_values = {key: round(value, 4) for key, value in totals.items()}
        gross_total = total_values["gross_value"]
        marginal_total = total_values["marginal_cost"]
        fully_loaded_total = total_values["fully_loaded_cost"]
        total_values.update(
            {
                "roi_marginal": round(
                    total_values["net_value_marginal"] / marginal_total, 4
                )
                if marginal_total
                else None,
                "roi_fully_loaded": round(
                    total_values["net_value_fully_loaded"] / fully_loaded_total, 4
                )
                if fully_loaded_total
                else None,
                "value_cost_ratio_marginal": round(gross_total / marginal_total, 4)
                if marginal_total
                else None,
                "value_cost_ratio_fully_loaded": round(
                    gross_total / fully_loaded_total, 4
                )
                if fully_loaded_total
                else None,
            }
        )
        scenarios[scenario] = {"runs": rows, "totals": total_values}
    reconciliation_error = round(
        sum(abs(float(run["child_cost"]) - step_cost[str(run["run_id"])]) for run in runs),
        8,
    )
    return {
        "label": "SYNTHETIC MODEL CHECK / NOT BUSINESS EVIDENCE",
        "evidence_level": "E0 EXPERT ESTIMATE",
        "business_task_count": len(run_ids),
        "status_denominator": len(runs),
        "status_counts": dict(Counter(str(run["run_status"]) for run in runs)),
        "gross_value_count": sum(1 for run in runs if float(run["success_weight"]) > 0),
        "child_cost_reconciliation_error": reconciliation_error,
        "scenarios": scenarios,
        "action": "VALIDATE",
    }
