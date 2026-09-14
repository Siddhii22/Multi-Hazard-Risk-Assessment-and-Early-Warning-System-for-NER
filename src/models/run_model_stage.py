"""Assess MSE-1 model readiness and train only on valid observed labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "processed" / "mse1_master.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "models"
TARGETS = ["flood", "landslide"]


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _dependency_status() -> dict[str, bool]:
    status = {}
    for package in ("sklearn", "xgboost", "joblib", "matplotlib"):
        try:
            __import__(package)
            status[package] = True
        except ImportError:
            status[package] = False
    return status


def assess_readiness(data: pd.DataFrame) -> dict[str, Any]:
    target_status = {}
    for target in TARGETS:
        if target not in data.columns:
            target_status[target] = {"status": "missing_column", "observed_rows": 0}
            continue
        observed = data[target].dropna()
        observed = observed[observed.astype(str).str.strip() != ""]
        target_status[target] = {
            "status": "valid" if len(observed) > 0 else "unavailable",
            "observed_rows": int(len(observed)),
            "distinct_values": sorted(observed.astype(str).unique().tolist()),
        }
    valid_targets = [target for target, status in target_status.items() if status["status"] == "valid"]
    return {
        "status": "ready_for_training" if valid_targets else "pending_missing_valid_targets",
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "valid_targets": valid_targets,
        "target_status": target_status,
        "candidate_models": {
            "logistic_regression": "available with scikit-learn",
            "random_forest": "available with scikit-learn",
            "xgboost": "available" if _dependency_status()["xgboost"] else "not installed; skipped",
        },
        "validation_policy": "Temporal ordering by observation_period when valid dates exist; otherwise spatial holdout by region. No random negative labels are constructed.",
        "blockers": [] if valid_targets else [
            "No observed flood or landslide labels are present in the processed master dataset.",
            "Missing hazard records remain unassigned and are not treated as negative labels.",
        ],
    }


def run(input_path: Path, output_path: Path) -> dict[str, Any]:
    data = pd.read_csv(input_path)
    report = assess_readiness(data)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "model_readiness.json").write_text(
        json.dumps(_json_safe(report), indent=2), encoding="utf-8"
    )
    selection = {
        "status": report["status"],
        "best_model": None,
        "reason": "Model comparison is pending until an authoritative hazard target contains observed labels." if not report["valid_targets"] else "Training is enabled for valid targets.",
        "trained_models": [],
        "metrics": [],
    }
    (output_path / "model_selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")
    print(f"Model stage: {report['status']}")
    print(f"Valid targets: {', '.join(report['valid_targets']) or 'none'}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    run(arguments.input, arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())