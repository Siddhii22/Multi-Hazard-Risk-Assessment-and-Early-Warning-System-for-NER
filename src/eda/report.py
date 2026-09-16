"""Generate reproducible MSE-1 EDA tables and presentation-ready charts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "processed" / "final_dataset_features.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "eda"


def run_eda(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> None:
    data = pd.read_csv(input_path, parse_dates=["date"], low_memory=False)
    output_path.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    numeric = data.select_dtypes(include="number")
    sample = data.sample(min(len(data), 100_000), random_state=42)

    overview = pd.DataFrame([{"rows": len(data), "columns": len(data.columns), "cells": data["cell_id"].nunique(), "date_min": data["date"].min(), "date_max": data["date"].max(), "flood_positive": int(data["flood_label"].sum()), "landslide_daily_positive": int(data["landslide_label_daily"].sum()), "landslide_static_positive": int(data["landslide_label_static"].sum())}])
    overview.to_csv(output_path / "dataset_overview.csv", index=False)
    missing = pd.DataFrame({"column": data.columns, "missing_count": data.isna().sum().values})
    missing["missing_percent"] = (missing["missing_count"] / len(data) * 100).round(4)
    missing.to_csv(output_path / "missing_values.csv", index=False)
    data.duplicated(["cell_id", "date"]).value_counts().rename_axis("is_duplicate_key").reset_index(name="count").to_csv(output_path / "duplicate_analysis.csv", index=False)
    numeric.describe().T.to_csv(output_path / "numeric_summary.csv")
    categorical_summary = data.select_dtypes(exclude="number").nunique(dropna=False).rename("unique_values").reset_index()
    categorical_summary.columns = ["column", "unique_values"]
    categorical_summary.to_csv(output_path / "categorical_summary.csv", index=False)
    numeric.corr().round(4).to_csv(output_path / "correlations.csv")
    data.groupby(data["date"].dt.month)["rain_1d_mm"].agg(["count", "mean", "sum"]).to_csv(output_path / "monthly_rainfall.csv")
    data.groupby("season")["rain_1d_mm"].agg(["count", "mean", "sum"]).to_csv(output_path / "seasonal_rainfall.csv")
    data.groupby("cell_id").agg(latitude=("latitude", "first"), longitude=("longitude", "first"), flood_frequency=("flood_label", "mean"), landslide_susceptibility=("landslide_label_static", "first")).reset_index().to_csv(output_path / "spatial_hazard_frequency.csv", index=False)

    def save_hist(column: str, filename: str) -> None:
        if column not in sample:
            return
        values = sample[column].dropna()
        if values.empty:
            return
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.histplot(values, bins=40, ax=ax, color="#167c80")
        ax.set_title(column)
        fig.tight_layout()
        fig.savefig(output_path / filename, dpi=140)
        plt.close(fig)

    for column in ["rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "elevation", "slope", "TWI", "SPI", "ndvi", "distance_to_river_km", "distance_to_road_km"]:
        save_hist(column, f"distribution_{column}.png")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for axis, target, title in zip(axes, ["flood_label", "landslide_label_daily", "landslide_label_static"], ["Flood labels", "Daily landslide labels", "Static susceptibility"]):
        data[target].value_counts().sort_index().plot.bar(ax=axis, color=["#d8dedb", "#d36b42"])
        axis.set_title(title)
        axis.set_xlabel("class")
        axis.set_ylabel("observations")
    fig.tight_layout()
    fig.savefig(output_path / "label_distributions.png", dpi=140)
    plt.close(fig)

    for column in ["rain_1d_mm", "rain_3d_mm", "rain_7d_mm"]:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.boxplot(data=sample, x="flood_label", y=column, showfliers=False, ax=ax, color="#8fbfba")
        ax.set_title(f"{column} by flood label")
        fig.tight_layout()
        fig.savefig(output_path / f"flood_vs_{column}.png", dpi=140)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(numeric.corr(), cmap="crest", center=0, ax=ax)
    fig.tight_layout()
    fig.savefig(output_path / "correlation_heatmap.png", dpi=140)
    plt.close(fig)
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