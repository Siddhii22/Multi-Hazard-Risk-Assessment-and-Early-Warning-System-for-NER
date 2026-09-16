# Data Dictionary

The authoritative input is `data/master_dataset_FINAL_v4.csv`. Static fields repeat across dates; rainfall support information and labels are observation-level. Missing values are genuine missingness and are not fabricated.

## Core schema

| Name | Type | Role / description | Dynamic or static |
|---|---|---|---|
| `cell_id` | string | Stable spatial cell identifier | Static |
| `date` | date | Daily observation date | Dynamic |
| `latitude`, `longitude` | float | Cell coordinates | Static |
| `soil_type_code`, `soil_type` | int/string | Soil classification | Static |
| `elevation`, `slope`, `aspect` | float | Terrain predictors; aspect is circular | Static |
| `TWI`, `SPI` | float | Terrain/hydrological indices | Static |
| `rain_1d_mm` | float | Daily rainfall | Dynamic |
| `station_count`, `interpolation_method` | int/string | Rainfall support and interpolation metadata | Dynamic/context |
| `distance_to_river_km`, `distance_to_road_km` | float | Hydrological and infrastructure proximity | Static |
| `ndvi`, `land_cover_class` | float | Land-surface predictors with genuine missingness | Static/context |
| `flood_label` | int | Primary dynamic supervised flood target | Dynamic label |
| `landslide_label_daily` | int | Sparse daily label; not currently modelled | Dynamic label |
| `landslide_label_static` | int | Spatial susceptibility component | Static label |
| `population_2011`, `households_2011` | float | Exposure variables | Static |
| `literacy_rate_2011`, `work_participation_rate_2011` | float | Socioeconomic vulnerability context | Static |

## Conventions

- All input sources are retained at native resolution during ingestion.
- All grid aggregation/intersection methods, CRS transformations, units, source versions, and access dates must be recorded.
- Do not imply that a resampled or aggregated feature is more precise than its source.
- Fit preprocessing transformations on training data only after a validation strategy is defined.

Generated fields include rainfall accumulation and previous windows, circular aspect transforms, temporal fields, and availability indicators. Their transformations are recorded in `data/processed/preprocessing_summary.json`.
