"""Build the reproducible MSE-1 master dataset from available boundary data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_ROOT = ROOT / "data" / "raw" / "geographic" / "openstreetmap" / "boundaries"
OUTPUT_ROOT = ROOT / "data" / "processed"
GRID_SIZE = 0.1

MASTER_COLUMNS = [
    "cell_id", "region", "latitude", "longitude", "observation_period",
    "rain_3h", "rain_24h", "rain_3d", "rain_7d", "elevation", "slope",
    "aspect", "NDVI", "NDWI", "distance_to_river_km", "distance_to_road_km",
    "population_density", "flood", "landslide",
]


def _read_boundary(path: Path) -> tuple[str, list[list[float]]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    feature = document["features"][0]
    properties = feature.get("properties", {})
    region = properties.get("name") or path.stem.split("_")[0].title()
    coordinates = feature["geometry"]["coordinates"][0]
    return str(region), coordinates


def _point_in_polygon(longitude: float, latitude: float, polygon: list[list[float]]) -> bool:
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x1, y1 = previous
        x2, y2 = current
        crosses = (y1 > latitude) != (y2 > latitude)
        if crosses and longitude < (x2 - x1) * (latitude - y1) / (y2 - y1) + x1:
            inside = not inside
        previous = current
    return inside


def _grid_values(polygon: list[list[float]]) -> Iterable[tuple[float, float]]:
    longitudes = [point[0] for point in polygon]
    latitudes = [point[1] for point in polygon]
    minimum_longitude = math.floor(min(longitudes) / GRID_SIZE) * GRID_SIZE
    maximum_longitude = math.ceil(max(longitudes) / GRID_SIZE) * GRID_SIZE
    minimum_latitude = math.floor(min(latitudes) / GRID_SIZE) * GRID_SIZE
    maximum_latitude = math.ceil(max(latitudes) / GRID_SIZE) * GRID_SIZE
    latitude = minimum_latitude + GRID_SIZE / 2
    while latitude < maximum_latitude:
        longitude = minimum_longitude + GRID_SIZE / 2
        while longitude < maximum_longitude:
            if _point_in_polygon(longitude, latitude, polygon):
                yield round(latitude, 6), round(longitude, 6)
            longitude += GRID_SIZE
        latitude += GRID_SIZE


def build_dataset() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    rows: list[dict[str, Any]] = []
    sources: list[dict[str, str]] = []
    for boundary_path in sorted(BOUNDARY_ROOT.glob("*.geojson")):
        region, polygon = _read_boundary(boundary_path)
        sources.append({"region": region, "path": str(boundary_path.relative_to(ROOT)), "format": "GeoJSON Polygon"})
        for latitude, longitude in _grid_values(polygon):
            row = {column: "" for column in MASTER_COLUMNS}
            row.update({
                "cell_id": f"{latitude:.3f}_{longitude:.3f}",
                "region": region,
                "latitude": latitude,
                "longitude": longitude,
            })
            rows.append(row)
    rows.sort(key=lambda row: (row["region"], row["latitude"], row["longitude"]))
    return rows, sources


def _write_geojson(rows: list[dict[str, Any]], path: Path) -> None:
    features = []
    half = GRID_SIZE / 2
    for row in rows:
        latitude = float(row["latitude"])
        longitude = float(row["longitude"])
        ring = [
            [longitude - half, latitude - half], [longitude + half, latitude - half],
            [longitude + half, latitude + half], [longitude - half, latitude + half],
            [longitude - half, latitude - half],
        ]
        features.append({"type": "Feature", "properties": row, "geometry": {"type": "Polygon", "coordinates": [ring]}})
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_ROOT)
    arguments = parser.parse_args()
    rows, sources = build_dataset()
    if not rows:
        raise RuntimeError(f"No boundary cells found under {BOUNDARY_ROOT}")
    arguments.output.mkdir(parents=True, exist_ok=True)
    with (arguments.output / "mse1_master.csv").open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=MASTER_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    _write_geojson(rows, arguments.output / "mse1_master_grid.geojson")
    availability = {
        "status": "partial_mse1_dataset",
        "grid": "0.1-degree cell centres retained when inside the supplied state boundary polygons",
        "real_sources_used": sources,
        "unavailable_sources": [
            "NASA GPM IMERG rainfall", "ISRO Bhuvan flood labels", "ISRO Bhuvan landslide labels",
            "SRTM terrain", "Sentinel-1/Sentinel-2 indices", "WorldPop population",
            "OSM river and road features (only boundary polygons are available)",
        ],
        "label_policy": "flood and landslide are blank because no authoritative event records are available; blanks are not negative labels",
    }
    (arguments.output / "mse1_data_availability.json").write_text(json.dumps(availability, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} cells to {arguments.output / 'mse1_master.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())