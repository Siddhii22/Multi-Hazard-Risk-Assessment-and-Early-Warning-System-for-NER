"""Describe future flood and spatial-susceptibility model pipelines without fitting them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "processed" / "final_dataset_features.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "models"


def candidate_pipelines(data: pd.DataFrame) -> dict[str, Pipeline]:
    excluded = {"cell_id", "date", "flood_label", "landslide_label_daily", "landslide_label_static"}
    features = [column for column in data.columns if column not in excluded]
    numeric = [column for column in features if pd.api.types.is_numeric_dtype(data[column])]
    categorical = [column for column in features if column not in numeric]
    transformer = ColumnTransformer([("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric), ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical)])
    return {"logistic_regression": Pipeline([("preprocess", transformer), ("model", LogisticRegression(max_iter=500, class_weight="balanced"))]), "random_forest": Pipeline([("preprocess", transformer), ("model", RandomForestClassifier(n_estimators=300, class_weight="balanced_subsample", random_state=42, n_jobs=-1))])}


def build_report(data: pd.DataFrame) -> dict[str, Any]:
    xgb_available = False
    try:
        import xgboost  # noqa: F401
        xgb_available = True
    except ImportError:
        pass
    return {"status": "identification_only", "dataset": str(DEFAULT_INPUT.relative_to(ROOT)), "targets": {"flood_label": {"role": "primary dynamic supervised target", "positive_observations": int(data["flood_label"].sum())}, "landslide_label_static": {"role": "spatial susceptibility component; not a daily warning target", "positive_observations": int(data["landslide_label_static"].sum())}, "landslide_label_daily": {"role": "not modelled because the positive class is too sparse", "positive_observations": int(data["landslide_label_daily"].sum())}}, "candidate_models": {"Logistic Regression": "scaled, interpretable baseline", "Random Forest": "nonlinear tabular baseline with interactions", "XGBoost": "gradient-boosted nonlinear comparison" if xgb_available else "optional candidate; dependency not installed"}, "metrics": ["precision", "recall", "F1", "PR-AUC", "ROC-AUC", "confusion matrix", "false-negative analysis"], "validation": "Use temporal ordering and spatial holdouts where feasible; fit imputers and encoders on training data only.", "trained": False, "results": []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    data = pd.read_csv(arguments.input, low_memory=False)
    arguments.output.mkdir(parents=True, exist_ok=True)
    (arguments.output / "model_identification.json").write_text(json.dumps(build_report(data), indent=2), encoding="utf-8")
    print(f"Wrote model identification to {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())