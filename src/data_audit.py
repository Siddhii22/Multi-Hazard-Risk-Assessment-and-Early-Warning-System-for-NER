"""Audit the immutable final daily dataset and write machine-readable reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "master_dataset_FINAL_v4.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "data_audit"


def _json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def audit_dataset(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    data = pd.read_csv(input_path, low_memory=False)
    parsed_dates = pd.to_datetime(data["date"], errors="coerce") if "date" in data else pd.Series(dtype="datetime64[ns]")
    missing = data.isna().sum()
    report: dict[str, Any] = {
        "dataset": str(input_path.relative_to(ROOT) if input_path.is_relative_to(ROOT) else input_path),
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "column_names": list(data.columns),
        "dtypes": {column: str(dtype) for column, dtype in data.dtypes.items()},
        "missing": {column: int(value) for column, value in missing.items()},
        "missing_percentage": {column: round(float(value / len(data) * 100), 4) for column, value in missing.items()},
        "duplicate_rows": int(data.duplicated().sum()),
        "duplicate_cell_date_keys": int(data.duplicated(["cell_id", "date"]).sum()),
        "unique_cells": int(data["cell_id"].nunique()),
        "date_range": {"min": parsed_dates.min().date().isoformat(), "max": parsed_dates.max().date().isoformat()},
        "numerical_ranges": {},
        "categorical_cardinality": {},
        "targets": {},
        "spatial_coverage": {},
        "temporal_coverage": {"unique_dates": int(parsed_dates.nunique()), "rows_per_date_min": int(data["date"].value_counts().min()), "rows_per_date_max": int(data["date"].value_counts().max())},
    }
    numeric = data.select_dtypes(include="number")
    for column in numeric.columns:
        report["numerical_ranges"][column] = {"min": _json_value(numeric[column].min()), "max": _json_value(numeric[column].max())}
    for column in data.select_dtypes(exclude="number").columns:
        report["categorical_cardinality"][column] = int(data[column].nunique(dropna=True))
    for target in ["flood_label", "landslide_label_daily", "landslide_label_static"]:
        if target in data:
            counts = data[target].value_counts(dropna=False).to_dict()
            report["targets"][target] = {str(_json_value(key)): int(value) for key, value in counts.items()}
    for column in ["latitude", "longitude"]:
        if column in data:
            report["spatial_coverage"][column] = {"min": float(data[column].min()), "max": float(data[column].max()), "unique": int(data[column].nunique())}

    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "audit_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    pd.DataFrame({"column": data.columns, "dtype": [str(dtype) for dtype in data.dtypes], "missing_count": missing.values, "missing_percentage": (missing / len(data) * 100).round(4), "unique_values": [data[column].nunique(dropna=True) for column in data.columns]}).to_csv(output_path / "column_summary.csv", index=False)
    pd.DataFrame([{"column": column, "min": values["min"], "max": values["max"]} for column, values in report["numerical_ranges"].items()]).to_csv(output_path / "numerical_ranges.csv", index=False)
    target_rows = [{"target": target, "class": label, "count": count} for target, values in report["targets"].items() for label, count in values.items()]
    pd.DataFrame(target_rows).to_csv(output_path / "target_distribution.csv", index=False)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    report = audit_dataset(arguments.input, arguments.output)
    print(f"Audited {report['rows']:,} rows and {report['columns']} columns")
    print(f"Wrote audit reports to {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())