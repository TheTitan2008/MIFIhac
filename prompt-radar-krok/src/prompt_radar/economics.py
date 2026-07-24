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
                "marginal_cost": round(marginal, 4),
                "fully_loaded_cost": round(fully_loaded, 4),
                "net_value_marginal": round(gross - marginal, 4),
                "net_value_fully_loaded": round(gross - fully_loaded, 4),
                "realized_net_saved_minutes": round(
                    baseline * success * quality - touch_minutes, 4
                ),
            }
            rows.append(row)
            totals.update({key: value for key, value in row.items() if key != "run_id"})
        scenarios[scenario] = {"runs": rows, "totals": {k: round(v, 4) for k, v in totals.items()}}
    reconciliation_error = round(
        sum(abs(float(run["child_cost"]) - step_cost[str(run["run_id"])]) for run in runs),
        8,
    )
    return {
        "label": "SYNTHETIC MODEL CHECK / NOT BUSINESS EVIDENCE",
        "evidence_level": "E0 EXPERT ESTIMATE",
        "business_task_count": len({str(run["run_id"]) for run in runs}),
        "status_denominator": len(runs),
        "status_counts": dict(Counter(str(run["run_status"]) for run in runs)),
        "gross_value_count": sum(1 for run in runs if float(run["success_weight"]) > 0),
        "child_cost_reconciliation_error": reconciliation_error,
        "scenarios": scenarios,
        "action": "VALIDATE",
    }
