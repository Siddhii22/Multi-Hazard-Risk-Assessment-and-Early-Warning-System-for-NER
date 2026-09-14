# AI and GIS-Based Multi-Hazard Risk Assessment and Early-Warning System for North-East India

## Project overview

This college project will develop an AI- and GIS-supported system to assess and communicate multi-hazard risk in Assam and Meghalaya. The system will keep hazard likelihood, rainfall severity, and population exposure distinct before combining them later in a documented risk engine.

## Problem and study region

Assam and Meghalaya are exposed to extreme rainfall, flood / flash flood, and landslide hazards. The project will create two initial prediction tasks—flood likelihood and landslide likelihood—on a common modelling grid, then later combine their outputs with rainfall severity and exposure information for multi-hazard risk communication.

## MSE-1 data design

- **Spatial unit:** an approximately 0.1-degree (~10 km) common grid, chosen for the prototype because GPM IMERG is approximately 0.1 degree. Each cell will have a stable `cell_id` and retained latitude/longitude. Resampling rainfall to a finer grid will never be represented as finer rainfall information.
- **Temporal unit:** event-based observations rather than a forced daily master table. Event dates or periods will be retained only when supplied by the source.
- **Rainfall windows:** `rain_3h`, `rain_24h`, `rain_3d`, and `rain_7d`, calculated immediately before the relevant event/observation period when the source supports it.
- **Initial predictors:** rainfall windows, elevation, slope, aspect, NDVI, NDWI, distance to river, distance to road, and population density.
- **Candidate models:** Logistic Regression baseline, Random Forest primary candidate, and XGBoost tabular comparison for both prediction tasks. No model has been trained.

## Target definitions

- **Flood target:** binary flood occurrence. `flood = 1` when a grid cell is associated with an observed flood/inundation event in the selected authoritative source and its available spatial/temporal information.
- **Landslide target:** binary landslide occurrence. `landslide = 1` when a grid cell is associated with an observed landslide event in the selected authoritative inventory and its available spatial/temporal information.
- A missing record is not automatically a negative label. Negative-sample construction remains open until the selected sources are inspected.
- Extreme rainfall is initially a predictor and later a trigger/risk-engine component, not a separate supervised ML target.

## Planned pipeline

1. Inspect candidate sources and record their metadata, coverage, and suitability.
2. Ingest sources at native resolution and construct documented grid-level features.
3. Build event-linked flood and landslide labels, including an explicit negative-sample design.
4. Perform EDA and select appropriate preprocessing.
5. Train, tune, and evaluate flood- and landslide-likelihood models using leakage-aware validation.
6. At ESE, combine flood probability, landslide probability, rainfall severity, and population/exposure into a composite multi-hazard risk score.
7. Produce GIS risk maps, red-zone identification, early-warning logic, and an interactive dashboard.

## Validation and spatial policy

Validation will not use a naive random split without considering spatial and temporal dependence. The eventual strategy will preserve temporal ordering where appropriate, apply spatial holdout/separation where feasible, and retain an untouched final test set. Future rainfall must never be used to predict a historical event, and preprocessing transformations must be fitted on training data only.

Spatial operations such as distance and area calculations will use appropriate CRS transformations. Source data will remain at native resolution during ingestion and be aggregated/intersected to the common grid during feature construction, with every aggregation method documented. CRS will not be mixed silently, and aggregation will not be described as creating information finer than a source dataset.

## Academic development stages

### MSE-1

- Problem identification and data design
- Dataset planning and source inspection
- Data preprocessing and EDA
- Model identification

### MSE-2

- Model training
- Hyperparameter tuning
- Result analysis

### ESE

- Working prediction/risk system
- Multi-hazard risk engine
- GIS risk map and red-zone identification
- Early-warning logic
- Interactive web dashboard and deployment

## Current status

Only project structure and planning documentation exist. No datasets have been collected or downloaded; no pipeline, models, results, maps, or predictions have been created.

## Data-ingestion scaffold

- `data/raw/` is for immutable acquired source files; `data/interim/` is reserved for temporary, reproducible intermediate outputs; and `data/processed/` is reserved for approved modelling-ready outputs. All three are Git-ignored except their placeholders.
- [config/project.toml](config/project.toml) holds repository-relative paths and study-region settings.
- [config/dataset_manifest.json](config/dataset_manifest.json) is a source-schema template. Its unknown source-specific fields are deliberately left as `TBD` or empty until source metadata is inspected.
- `src/data_ingestion/validate_dataset.py` performs read-only, manifest-driven structural and CSV-column checks after an acquired dataset is placed in its configured raw-data directory. It does not download, transform, or create data.

## Open decisions after source inspection

- Exact event-date/period handling for each source
- Negative-sample construction for flood and landslide targets
- Exact available coverage period
- Final train/validation/test periods and spatial holdout design
- Dataset-specific aggregation/intersection method
- Confirmed source licences, access methods, formats, metadata, resolution, and target suitability
