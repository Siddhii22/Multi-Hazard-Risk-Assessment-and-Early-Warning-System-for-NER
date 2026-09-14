"""Validate an acquired dataset against its configured manifest entry.

This utility never downloads, transforms, or writes dataset content. Schema checks
become active only after source-specific expectations are added to the manifest.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPOSITORY_ROOT / "config" / "dataset_manifest.json"
DEFAULT_RAW_ROOT = REPOSITORY_ROOT / "data" / "raw"


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load and minimally validate the JSON manifest."""
    with manifest_path.open(encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)
    if not isinstance(manifest.get("datasets"), list):
        raise ValueError("Manifest must contain a 'datasets' list.")
    return manifest


def find_dataset(manifest: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    """Return one manifest dataset by stable identifier."""
    for dataset in manifest["datasets"]:
        if dataset.get("id") == dataset_id:
            return dataset
    raise KeyError(f"Dataset id '{dataset_id}' is not present in the manifest.")


def _csv_columns(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, None)
    return set(header or [])


def validate_dataset(dataset: dict[str, Any], dataset_path: Path) -> dict[str, Any]:
    """Check file structure and configured CSV fields without changing any files."""
    report: dict[str, Any] = {
        "dataset_id": dataset["id"],
        "path": str(dataset_path),
        "valid": True,
        "errors": [],
        "warnings": [],
    }

    if not dataset_path.exists():
        report["valid"] = False
        report["errors"].append("Dataset path does not exist.")
        return report

    files = [dataset_path] if dataset_path.is_file() else [path for path in dataset_path.rglob("*") if path.is_file()]
    if not files:
        report["valid"] = False
        report["errors"].append("Dataset path contains no files.")
        return report

    for required_path in dataset.get("required_paths", []):
        if not (dataset_path / required_path).exists():
            report["valid"] = False
            report["errors"].append(f"Missing required path: {required_path}")

    allowed_extensions = {extension.lower() for extension in dataset.get("expected_file_extensions", [])}
    if allowed_extensions:
        invalid_files = [str(path) for path in files if path.suffix.lower() not in allowed_extensions]
        if invalid_files:
            report["valid"] = False
            report["errors"].append(f"Unexpected file extension(s): {invalid_files}")
    else:
        report["warnings"].append("Expected file extensions are not configured; file-type validation was skipped.")

    required_columns = set(dataset.get("required_columns", []))
    if required_columns:
        csv_files = [path for path in files if path.suffix.lower() == ".csv"]
        if not csv_files:
            report["valid"] = False
            report["errors"].append("Required columns are configured, but no CSV file was found for column validation.")
        for csv_path in csv_files:
            missing = sorted(required_columns - _csv_columns(csv_path))
            if missing:
                report["valid"] = False
                report["errors"].append(f"{csv_path.name} is missing required columns: {missing}")
    else:
        report["warnings"].append("Required columns are not configured; schema validation was skipped.")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an acquired dataset against config/dataset_manifest.json.")
    parser.add_argument("dataset_id", help="Stable dataset identifier from the manifest.")
    parser.add_argument("--path", type=Path, help="Dataset file or directory. Defaults to its configured raw-data directory.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to the dataset manifest JSON file.")
    arguments = parser.parse_args()

    try:
        dataset = find_dataset(load_manifest(arguments.manifest), arguments.dataset_id)
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)], "warnings": []}, indent=2))
        return 2

    dataset_path = arguments.path or DEFAULT_RAW_ROOT / dataset["raw_subdirectory"]
    report = validate_dataset(dataset, dataset_path)
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
