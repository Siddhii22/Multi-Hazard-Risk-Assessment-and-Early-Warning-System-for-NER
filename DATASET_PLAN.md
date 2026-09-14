# Dataset Plan

The listed sources are priorities for inspection, not collection commitments. No source is assumed to be required for the first dataset version. Before collection, inspect actual coverage, temporal availability, spatial resolution, licence/access, format, metadata, and suitability for the target definition.

## Data sources and intended use

| Data category | Intended role | Priority source to inspect | Planned grid-level output | Status |
|---|---|---|---|---|
| Rainfall dataset | Event-preceding rainfall predictors; later severity/trigger component | NASA GPM IMERG Final V07 | `rain_3h`, `rain_24h`, `rain_3d`, `rain_7d` when temporally supported | Not collected / not inspected |
| Flood labels | Binary flood occurrence target | ISRO Bhuvan flood products | `flood = 1` for documented event-cell associations | Not collected / not inspected |
| Landslide labels | Binary landslide occurrence target | ISRO Bhuvan landslide inventory | `landslide = 1` for documented event-cell associations | Not collected / not inspected |
| Terrain features | Static susceptibility predictors | SRTM DEM | elevation, slope, aspect | Not collected / not inspected |
| Satellite-derived features | Environmental predictors where justified | Sentinel-1 / Sentinel-2 | NDVI, NDWI where supported and justified | Not collected / not inspected |
| River / road features | Proximity predictors | OpenStreetMap | `distance_to_river_km`, `distance_to_road_km` | Not collected / not inspected |
| Population exposure | Exposure component for later risk engine | WorldPop | population density | Not collected / not inspected |

## Source Inspection Summary

Public documentation was inspected on 14 September 2026 only; no data or metadata files were downloaded. Product-specific metadata must still be checked before source selection.

| Priority source | What it provides | Spatial resolution | Temporal coverage / frequency | Event dates or observation periods | Access / download feasibility | Major project limitations |
|---|---|---|---|---|---|---|
| [NASA GPM IMERG Final V07](https://gpm.nasa.gov/taxonomy/term/1417) | Satellite-gauge precipitation estimates and accumulation products | 0.1° × 0.1° (about 10 km) | Record from January 1998 to present; native half-hourly products, with other accumulations available | Yes: time-stamped precipitation observations/products support preceding-rainfall windows; Final Run has roughly 3.5-month latency | Available through NASA PPS/GES DISC in formats including HDF5, GeoTIFF, and NetCDF; free registration is documented | Satellite precipitation uncertainty, coarse grid, and Final-Run latency; no finer rainfall information is created by resampling |
| [ISRO Bhuvan flood products](https://bhuvan.nrsc.gov.in/wiki/index.php/Thematic_Data) | Flood hazard and flood annual thematic layers; Bhuvan documentation identifies Assam annual layers for 1998–2010 | Public Bhuvan catalogue lists flood annual layers at 1:250,000 scale; native pixel/feature resolution requires product metadata | Annual layers are documented for 1999–2010 (one Bhuvan update says Assam 1998–2010); no operational frequency confirmed for the proposed label source | Annual observation periods are indicated; exact flood-event dates are not established by the inspected documentation | Visualisation and OGC WMS/WMTS access are documented; direct machine-download/export feasibility for the required layers remains to be verified | Historical/annual coverage may be unsuitable for event-linked labels; scale is not a pixel resolution; date, geometry, and current Assam/Meghalaya coverage need inspection |
| [ISRO Bhuvan landslide inventory](https://bhuvan-app1.nrsc.gov.in/disaster/usrtasks/landslide/landslide.php?uname=empty) | Landslide inventory layers, including event-based and seasonal inventories; NRSC reports an atlas database of about 80,000 landslides mapped during 1998–2022 | Not stated in the inspected public inventory summary; inventory geometry and mapping resolution must be checked in metadata | Mixed: portal shows seasonal inventory for Assam and Meghalaya in 2014, and separate event inventories; atlas reporting spans 1998–2022 | Some portal inventories explicitly identify a season or event period; event-date field availability for Assam/Meghalaya records is unresolved | Public Bhuvan portal provides map/metadata/web-service links; downloadable record-level access and licence must be verified | Satellite mapping can be limited by resolution, cloud cover, and shadow; heterogeneous inventory types and uncertain per-record dates complicate event labels and negative samples |
| [SRTM DEM](https://www.earthdata.nasa.gov/centers/lp-daac) | Elevation DEM; slope and aspect can later be derived | SRTMGL1.003 is 30 m | Single Shuttle mission acquisition in February 2000 (11-day mission); static terrain input | No hazard-event dates; acquisition is a fixed observation period | Publicly catalogued by NASA Earthdata/LP DAAC; collection-level access is feasible, but the exact access path/account requirement should be confirmed before collection | Represents terrain at one mission period; voids/artefacts and DEM-derived slope/aspect method still need assessment; not contemporaneous hazard evidence |
| [Copernicus Sentinel-1 / Sentinel-2](https://dataspace.copernicus.eu/) | Sentinel-1 SAR backscatter for all-weather surface observation; Sentinel-2 multispectral imagery supporting NDVI/NDWI | Sentinel-1 IW: 5 × 20 m geometric resolution (common GRD access products may use 10 m pixel spacing); Sentinel-2: 10 m, 20 m, and 60 m bands | Sentinel-1 GRD archive: October 2014–present; Sentinel-2 design revisit: 5 days at the Equator | Yes: scene-level acquisition timestamps are available, subject to product selection and catalogue inspection | Copernicus Data Space offers free/open mission data access; account/API/export method and actual regional availability must be checked | Sentinel-1 needs SAR-specific processing and terrain considerations; Sentinel-2 optical observations are cloud-limited, particularly relevant to monsoon events; neither should be assumed necessary for version one |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Volunteer-maintained vector road, waterway, and other mapped geographic features | Vector data; no uniform spatial resolution | Continuously edited; full planet snapshots are released weekly, with smaller extracts/diffs available | Edit/history timestamps exist, but they are not hazard observation dates | Downloadable through OSM data/extract services; reuse is under ODbL with attribution obligations | Completeness, tagging, positional accuracy, and update timing vary locally; historic road/river state at a past event may be unavailable; licence obligations require review |
| [WorldPop Global2 population](https://hub.worldpop.org/project/categories?id=3) | Gridded population counts; can support population-density/exposure aggregation | Individual-country products are offered at 100 m and 1 km; global mosaics at 1 km | Annual products for 2015–2030 | Dataset year is available, but it is not a hazard-event observation date | Open access through WorldPop data portal/API; exact India product, licence, and release metadata must be selected before collection | Modelled population estimates, not event-time exposure; year alignment and count-to-density aggregation must be decided; do not substitute a population year for an event date |

## Modelling and source-resolution policy

- MSE-1 will use an approximately 0.1-degree (~10 km) common modelling grid, aligned with the approximate resolution of GPM IMERG.
- Every grid cell must have a stable `cell_id` and retained latitude/longitude.
- Sources retain native resolution during ingestion. Feature construction will aggregate or intersect them onto the modelling grid using a documented source-specific method.
- Resampling or aggregation does not create information finer than a source dataset.
- Use appropriate CRS transformations for area and distance operations; do not mix CRS silently.
- Keep the first stable dataset intentionally small. Do not add predictors beyond the listed initial core set without evidence after source inspection.

## Label and time policy

- Use event-based modelling. Retain an event date or observation period only where the source provides it; never invent event dates.
- Calculate rainfall windows from the rainfall immediately preceding the relevant event/observation period where source data permits.
- A missing flood or landslide record does not constitute a negative label. Negative-sample construction will be explicitly designed after inspection.
- Extreme rainfall is not an initial supervised target; it is a predictor and later risk-engine/trigger component.

## Dataset acceptance checklist

- Appropriate coverage for Assam and Meghalaya.
- Documented source, version, licence, retrieval date, and attribution requirements.
- Known spatial and temporal resolution, format, metadata, and available period.
- Alignable to the modelling grid without overstating source precision.
- Supports the intended event/label definition and does not introduce target leakage.

## Open decisions after source inspection

- Exact event-date/period handling
- Negative-sample construction
- Exact coverage period
- Final train/validation/test periods
- Aggregation/intersection method for each dataset
