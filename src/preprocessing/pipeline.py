"""Create modelling-ready features without modifying the final raw CSV."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "master_dataset_FINAL_v4.csv"
DEFAULT_OUTPUT = ROOT / "data" / "processed"


def _season(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Pre-monsoon"
    if month in (6, 7, 8, 9):
        return "Monsoon"
    return "Post-monsoon"


def preprocess(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> pd.DataFrame:
    data = pd.read_csv(input_path, low_memory=False)
    data["date"] = pd.to_datetime(data["date"], errors="raise")
    data = data.drop_duplicates().sort_values(["cell_id", "date"], kind="mergesort").reset_index(drop=True)
    if data.duplicated(["cell_id", "date"]).any():
        raise ValueError("cell_id + date must be unique after exact duplicate removal")

    grouped = data.groupby("cell_id", sort=False)["rain_1d_mm"]
    data["rain_3d_mm"] = grouped.transform(lambda series: series.rolling(3, min_periods=1).sum())
    data["rain_7d_mm"] = grouped.transform(lambda series: series.rolling(7, min_periods=1).sum())
    data["rain_3d_prev_mm"] = data.groupby("cell_id", sort=False)["rain_1d_mm"].transform(lambda series: series.shift(1).rolling(3, min_periods=1).sum())
    data["rain_7d_prev_mm"] = data.groupby("cell_id", sort=False)["rain_1d_mm"].transform(lambda series: series.shift(1).rolling(7, min_periods=1).sum())
    radians = data["aspect"] * 3.141592653589793 / 180
    data["aspect_sin"] = radians.map(__import__("math").sin)
    data["aspect_cos"] = radians.map(__import__("math").cos)
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["day_of_year"] = data["date"].dt.dayofyear
    data["season"] = data["month"].map(_season)
    sparse_features = ["ndvi", "land_cover_class", "population_2011", "households_2011", "literacy_rate_2011", "work_participation_rate_2011"]
    for feature in sparse_features:
        if feature in data:
            data[f"{feature}_available"] = data[feature].notna().astype("int8")
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "final_dataset_features.csv"
    data.to_csv(output_file, index=False, date_format="%Y-%m-%d")
    metadata = {"source": str(input_path.relative_to(ROOT)), "output": str(output_file.relative_to(ROOT)), "rows": int(len(data)), "columns": int(len(data.columns)), "exact_duplicates_removed": int(pd.read_csv(input_path, low_memory=False).duplicated().sum()), "key_unique": True, "feature_engineering": ["rain_3d_mm", "rain_7d_mm", "rain_3d_prev_mm", "rain_7d_prev_mm", "aspect_sin", "aspect_cos", "year", "month", "day_of_year", "season", "sparse-feature availability indicators"], "imputation_policy": "No values are imputed in this artifact. Fit training-only imputers inside model pipelines."}
    (output_path / "preprocessing_summary.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote {len(data):,} rows and {len(data.columns)} columns to {output_file}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    preprocess(arguments.input, arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())