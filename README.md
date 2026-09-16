# Multi-Hazard Risk Assessment and Early-Warning System

## Problem and scope

This project develops a GIS- and AI-based environmental intelligence system for Assam and Meghalaya within the wider North-East India context. It integrates daily rainfall, terrain, hydrology, land-surface, soil, infrastructure, and socioeconomic exposure variables to support spatial hazard assessment and future early-warning decisions.

The current MSE-1 scope is dataset audit, reproducible preprocessing, exploratory analysis, model identification, and an interactive dashboard. It does not claim operational warnings, trained final models, or final multi-hazard risk scores.

## Dataset and objectives

`data/master_dataset_FINAL_v4.csv` is the authoritative, immutable input: 522,522 daily observations, 693 spatial cells, 25 columns, and coverage from 2021-01-08 to 2023-12-14. The primary supervised target is `flood_label` with 311 positive observations. `landslide_label_static` is treated as a spatial susceptibility component; `landslide_label_daily` has only six positives and is not used as a daily classifier target.

Objectives are to integrate heterogeneous variables, build reproducible preprocessing, analyse spatial and temporal patterns, prepare flood and susceptibility components, establish exposure-aware architecture, and provide interactive visual analysis for MSE-1 evaluation.

## Pipeline

1. `python -m src.data_audit`
2. `python -m src.preprocessing.pipeline`
3. `python -m src.eda.report`
4. `python -m src.model_identification`

The raw CSV is never overwritten. Preprocessing creates rainfall 3-day/7-day and previous-window features, circular aspect transforms, temporal fields, and sparse-feature availability indicators. Model imputers and encoders must be fitted on training data only.

## Model identification

Candidate models are Logistic Regression, Random Forest, and XGBoost. MSE-2 will use temporal and/or spatially aware validation, then report precision, recall, F1, PR-AUC, ROC-AUC, confusion matrices, and false-negative analysis. No model results are fabricated in MSE-1.

## Dashboard

Run from the repository root: `streamlit run dashboard/app.py`. Pages cover overview, study region, data and sources, preparation, interactive EDA, hazard intelligence, AI model lab, spatial intelligence, and an explicitly non-operational early-warning architecture.

## Future stages and limitations

MSE-2 adds training, tuning, spatial-temporal evaluation, explainability, and error analysis. ESE adds validated outputs, documented exposure/vulnerability combination, stakeholder-reviewed warning logic, and deployment. Current limitations include extreme flood imbalance, sparse daily landslide labels, missing socioeconomic coverage, and no validated operational warning threshold.

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
