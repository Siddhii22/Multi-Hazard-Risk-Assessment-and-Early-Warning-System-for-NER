"""Generate MSE-1 EDA outputs from the processed master dataset."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "processed" / "mse1_master.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "eda"


def _write_json(path: Path, value: Any) -> None:
    def clean(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: clean(child) for key, child in item.items()}
        if isinstance(item, list):
            return [clean(child) for child in item]
        if isinstance(item, float) and not math.isfinite(item):
            return None
        return item

    path.write_text(json.dumps(clean(value), indent=2, default=str, allow_nan=False), encoding="utf-8")


def _write_spatial_svg(data: pd.DataFrame, path: Path) -> None:
    width, height, padding = 1000, 650, 40
    min_x, max_x = data.longitude.min(), data.longitude.max()
    min_y, max_y = data.latitude.min(), data.latitude.max()
    x_span = max(max_x - min_x, 0.1)
    y_span = max(max_y - min_y, 0.1)

    def project(x: float, y: float) -> tuple[float, float]:
        return (padding + (x - min_x) / x_span * (width - 2 * padding),
                height - padding - (y - min_y) / y_span * (height - 2 * padding))

    circles = []
    for row in data.itertuples(index=False):
        x, y = project(float(row.longitude), float(row.latitude))
        circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#d95f02" opacity="0.7"/>')
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#f7f4ed"/>',
           '<text x="40" y="28" font-family="sans-serif" font-size="20" fill="#252525">MSE-1 processed grid cells</text>',
           *circles,
           f'<text x="40" y="{height - 14}" font-family="sans-serif" font-size="12" fill="#555">longitude / latitude cell-centre view; not a boundary map</text>', '</svg>']
    path.write_text("\n".join(svg), encoding="utf-8")


def run_eda(input_path: Path, output_path: Path) -> None:
    data = pd.read_csv(input_path)
    output_path.mkdir(parents=True, exist_ok=True)
    numeric = data.select_dtypes(include="number")
    summary = {
        "rows": int(len(data)), "columns": int(len(data.columns)),
        "column_names": list(data.columns), "regions": data["region"].value_counts().to_dict(),
        "numeric_summary": numeric.describe().round(6).to_dict(),
    }
    _write_json(output_path / "dataset_summary.json", summary)
    missing = pd.DataFrame({"column": data.columns, "missing_count": data.isna().sum().values + (data == "").sum().values})
    missing["missing_percent"] = (missing["missing_count"] / len(data) * 100).round(3)
    missing.to_csv(output_path / "missing_values.csv", index=False)
    distributions = []
    for column in numeric.columns:
        values = numeric[column].dropna()
        distributions.append({"feature": column, "count": int(values.count()), "min": values.min(), "max": values.max(), "mean": values.mean(), "median": values.median(), "std": values.std()})
    pd.DataFrame(distributions).to_csv(output_path / "feature_distributions.csv", index=False)
    numeric.corr().round(6).to_csv(output_path / "correlations.csv")
    for name, columns in {"rainfall_analysis": ["rain_3h", "rain_24h", "rain_3d", "rain_7d"], "terrain_population_analysis": ["elevation", "slope", "aspect", "population_density"]}.items():
        available = [column for column in columns if column in data and data[column].notna().any()]
        _write_json(output_path / f"{name}.json", {"status": "available" if available else "unavailable", "available_features": available, "reason": "No real source data is present in the processed dataset." if not available else ""})
    data.groupby("region", dropna=False).size().rename("cell_count").reset_index().to_csv(output_path / "cells_by_region.csv", index=False)
    _write_spatial_svg(data, output_path / "spatial_grid.svg")
    print(f"Wrote EDA outputs to {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    run_eda(arguments.input, arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())