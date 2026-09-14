# Data Dictionary

This is the authoritative record for every approved feature and label. Populate source-specific values only after inspection; no value below asserts that a source has been obtained or validated.

## Core schema

| Dataset / layer | Feature name | Description | Source | Unit | Data type | Native spatial resolution | Native temporal resolution | Grid aggregation method | Coverage period | Event-date handling | Preprocessing notes | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Modelling grid | `cell_id` | Stable identifier for approximately 0.1-degree (~10 km) modelling cell | Project grid | Identifier | String/integer | Approximately 0.1 degree | N/A | N/A | TBD | N/A | Retain representative latitude/longitude; CRS to be documented | Design decision |
| Modelling grid | `latitude`, `longitude` | Grid-cell location fields | Project grid | Decimal degrees | Float | Approximately 0.1 degree | N/A | N/A | TBD | N/A | Definition of representative point to be recorded | Design decision |
| Rainfall | `rain_3h` | Rainfall in the 3 hours preceding a source-supported event/observation period | NASA GPM IMERG Final V07 (planned inspection) | TBD | Numeric | TBD | TBD | TBD | TBD | TBD | Do not invent event dates | Planned |
| Rainfall | `rain_24h` | Rainfall in the 24 hours preceding a source-supported event/observation period | NASA GPM IMERG Final V07 (planned inspection) | TBD | Numeric | TBD | TBD | TBD | TBD | TBD | Do not invent event dates | Planned |
| Rainfall | `rain_3d` | Rainfall in the 3 days preceding a source-supported event/observation period | NASA GPM IMERG Final V07 (planned inspection) | TBD | Numeric | TBD | TBD | TBD | TBD | TBD | Do not invent event dates | Planned |
| Rainfall | `rain_7d` | Rainfall in the 7 days preceding a source-supported event/observation period | NASA GPM IMERG Final V07 (planned inspection) | TBD | Numeric | TBD | TBD | TBD | TBD | TBD | Do not invent event dates | Planned |
| Terrain | `elevation`, `slope`, `aspect` | Terrain predictors | SRTM DEM (planned inspection) | TBD | Numeric | TBD | Static | TBD | TBD | N/A | CRS and terrain derivation method to be documented | Planned |
| Satellite | `NDVI`, `NDWI` | Satellite-derived environmental predictors, if justified | Sentinel-1 / Sentinel-2 (planned inspection) | Index | Numeric | TBD | TBD | TBD | TBD | TBD | Sensor/product selection and method TBD | Planned |
| Geographic | `distance_to_river_km`, `distance_to_road_km` | Distance features to river and road networks | OpenStreetMap (planned inspection) | km | Numeric | Vector / TBD | TBD | TBD | TBD | N/A | Calculate in a suitable projected CRS | Planned |
| Exposure | `population_density` | Population exposure feature | WorldPop (planned inspection) | TBD | Numeric | TBD | TBD | TBD | TBD | TBD | Unit and aggregation method TBD | Planned |
| Flood label | `flood` | Binary observed flood/inundation occurrence label | ISRO Bhuvan flood products (planned inspection) | 0/1 | Integer | TBD | TBD | TBD | TBD | TBD | `1` only for documented event-cell association; negative construction TBD | Planned |
| Landslide label | `landslide` | Binary observed landslide occurrence label | ISRO Bhuvan landslide inventory (planned inspection) | 0/1 | Integer | TBD | TBD | TBD | TBD | TBD | `1` only for documented event-cell association; negative construction TBD | Planned |

## Conventions

- All input sources are retained at native resolution during ingestion.
- All grid aggregation/intersection methods, CRS transformations, units, source versions, and access dates must be recorded.
- Do not imply that a resampled or aggregated feature is more precise than its source.
- Fit preprocessing transformations on training data only after a validation strategy is defined.

## Open decisions after source inspection

- Exact event-date/period handling
- Negative-sample construction
- Exact coverage period
- Final train/validation/test periods
- Aggregation/intersection method for each dataset
