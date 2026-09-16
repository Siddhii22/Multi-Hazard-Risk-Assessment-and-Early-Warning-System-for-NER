# Project Decisions Log

The following are approved data-design decisions. `TBD` entries are intentionally deferred until actual source metadata is inspected.

| Decision area | Approved decision | Rationale / guardrails | Status |
|---|---|---|---|
| Spatial modelling unit | Common approximately 0.1-degree (~10 km) grid for the MSE-1 prototype | Matches approximate GPM IMERG resolution; each cell has stable `cell_id` and retained latitude/longitude. Finer resampling does not create finer rainfall information. | Approved |
| Temporal unit | Daily observations from the authoritative final dataset are used; dates are parsed and sorted by cell. | Approved |
| Rainfall features | `rain_3d_mm`, `rain_7d_mm`, and previous-window features exclude the current day to reduce leakage risk. | Approved |
| Flood target | `flood_label` is the primary dynamic supervised target; only 311 observations are positive. | Approved |
| Landslide target | `landslide_label_static` is a spatial susceptibility component; `landslide_label_daily` is too sparse for daily classification. | Approved |
| Extreme rainfall target | Rainfall is a predictor and future trigger component, not a separate supervised target. | Approved |
| Prediction architecture | Flood model candidate plus separate landslide susceptibility layer; future outputs may feed documented exposure-aware risk. | MSE-1 architecture |
| Candidate models | Logistic Regression baseline, Random Forest, and XGBoost comparison; no training results yet. | Approved |
| Initial feature scope | Rainfall windows, elevation, slope, aspect, NDVI, NDWI, river/road distances, population density | Keep MSE-1 deliberately small; add features only with post-inspection justification. | Approved |
| Validation strategy | Leakage-aware spatial-temporal evaluation | No naive random split alone; preserve time order where appropriate, use spatial holdout where feasible, preserve untouched final test data. | Approved principles; exact split open |
| Leakage prevention | No future rainfall for historical events; training-only fitting of preprocessing | Final feature availability must be checked against each event time. | Approved |
| CRS and resolution | Consistent grid; source-native ingestion; documented aggregation/intersection | Use appropriate projected CRS for distance/area operations; never silently mix CRS or claim enhanced source precision. | Approved |
| Data-source policy | Prioritise NASA GPM IMERG Final V07, ISRO Bhuvan flood/landslide products, SRTM, Sentinel-1/2, OpenStreetMap, and WorldPop | Inspect coverage, availability, resolution, licence/access, format, metadata, and target suitability before collection. Not every source is mandatory for version one. | Approved |

## Open decisions after source inspection

- Exact event-date and observation-period handling for each source
- Negative-sample construction for flood and landslide labels
- Exact available coverage period
- Final train/validation/test periods and spatial-holdout implementation
- Aggregation/intersection method for each dataset
- Final source inclusion, licences, access method, format, metadata quality, and target suitability

## Decision principles

- Prefer documented, reproducible choices and record dataset versions/access dates.
- Keep spatial and temporal leakage checks explicit.
- Keep hazard likelihood separate from exposure and the later risk-combination method.
