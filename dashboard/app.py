"""NE-Hazard Intelligence dashboard backed by the project's real outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = ROOT / "data" / "processed" / "mse1_master.csv"
AVAILABILITY_PATH = ROOT / "data" / "processed" / "mse1_data_availability.json"
EDA_ROOT = ROOT / "outputs" / "eda"
MODEL_ROOT = ROOT / "outputs" / "models"

st.set_page_config(page_title="NE-Hazard Intelligence", page_icon="N", layout="wide", initial_sidebar_state="expanded")


@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data
def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as input_file:
        return json.load(input_file)


def css() -> None:
    st.markdown("""
    <style>
    :root { --ink:#183234; --muted:#607477; --teal:#087f78; --gold:#d98b2b; --paper:#f4f7f5; }
    .stApp { background: #f4f7f5; color: var(--ink); }
    [data-testid="stSidebar"] { background: #163b3b; }
    [data-testid="stSidebar"] * { color: #eff8f4 !important; }
    [data-testid="stSidebar"] .stRadio label { padding: .25rem 0; }
    h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
    .hero { background: linear-gradient(120deg,#123e3d,#1e6860); color:white; padding:2.3rem 2.5rem; border-radius:8px; margin-bottom:1.4rem; }
    .hero h1 { color:white; font-size:2.35rem; line-height:1.12; margin:0 0 .55rem; }
    .hero p { color:#d9efea; font-size:1.03rem; max-width:850px; margin:0; }
    .eyebrow { color:#b9dfd4; font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.7rem; }
    .card { background:white; border:1px solid #dce8e3; border-radius:8px; padding:1.05rem 1.15rem; min-height:135px; }
    .card h4 { margin:0 0 .45rem; color:#173f40; }
    .card p { color:#607477; font-size:.88rem; margin:.25rem 0; }
    .tag { display:inline-block; padding:.18rem .5rem; border-radius:12px; font-size:.72rem; font-weight:700; background:#e1f2ec; color:#176358; }
    .tag.dim { background:#edf1ef; color:#697979; }
    .section-note { color:#607477; margin-top:-.45rem; margin-bottom:1rem; }
    .pipeline { display:flex; gap:.5rem; align-items:stretch; margin:1.2rem 0 1.6rem; }
    .step { flex:1; background:white; border-top:4px solid #16877c; padding:.85rem .8rem; border-radius:5px; box-shadow:0 1px 4px #173f4012; }
    .step b { display:block; font-size:.82rem; color:#173f40; }
    .step span { display:block; color:#718080; font-size:.75rem; margin-top:.3rem; }
    .arrow { align-self:center; color:#d98b2b; font-size:1.2rem; }
    .mini-title { text-transform:uppercase; letter-spacing:.08em; font-size:.72rem; color:#087f78; font-weight:800; }
    </style>
    """, unsafe_allow_html=True)


def table(data: pd.DataFrame, height: int = 320) -> None:
    st.dataframe(data, use_container_width=True, height=height, hide_index=True)


def metric_row(data: pd.DataFrame) -> None:
    cells, features = data.shape
    numeric = len(data.select_dtypes(include="number").columns)
    regions = data["region"].nunique()
    a, b, c, d = st.columns(4)
    a.metric("Grid cells", f"{cells:,}")
    b.metric("Current study states", regions)
    c.metric("Dataset fields", features)
    d.metric("Numeric fields", numeric)


def source_cards() -> None:
    sources = [
        ("Rainfall", "NASA GPM IMERG", "3 h / 24 h / 3 d / 7 d accumulation windows", "0.1° · half-hourly source", "To be integrated", False),
        ("Flood observations", "Bhuvan / authoritative flood inventory", "Observed flood-event labels", "Annual/event layers · coverage varies", "To be integrated", False),
        ("Landslide inventory", "Bhuvan / GSI inventory", "Observed landslide-event labels", "Event/season inventory · coverage varies", "To be integrated", False),
        ("Terrain", "SRTM DEM", "Elevation, slope, aspect", "30 m · static terrain", "Not populated in master", False),
        ("Satellite", "Sentinel-1 / Sentinel-2", "NDVI, NDWI, environmental indicators", "10–60 m products · scene-based", "To be integrated", False),
        ("Geographic features", "OpenStreetMap", "River and road proximity", "Vector · continuously edited", "Boundary polygons only", False),
        ("Population", "WorldPop", "Population exposure", "100 m / 1 km products · annual", "To be integrated", False),
    ]
    cols = st.columns(3)
    for index, (title, source, purpose, detail, status, available) in enumerate(sources):
        with cols[index % 3]:
            badge = "Integrated" if available else "Not yet integrated"
            dim = "" if available else "dim"
            st.markdown(f'<div class="card"><div class="mini-title">{title}</div><h4>{source}</h4><p>{purpose}</p><p><small>{detail}</small></p><span class="tag {dim}">{badge}</span><p><small>{status}</small></p></div>', unsafe_allow_html=True)


def regional_context_svg() -> str:
    # Geographic context only: no observations or values are encoded for future states.
    states = [("Arunachal Pradesh", 285, 75, False), ("Sikkim", 175, 215, False), ("Assam", 310, 220, True), ("Nagaland", 465, 245, False), ("Manipur", 470, 330, False), ("Meghalaya", 275, 345, True), ("Tripura", 215, 430, False), ("Mizoram", 375, 420, False)]
    shapes = []
    for name, x, y, current in states:
        fill = "#16877c" if current else "#c9d8d3"
        stroke = "#0b5b57" if current else "#8ba09a"
        text = "white" if current else "#294648"
        shapes.append(f'<rect x="{x}" y="{y}" width="110" height="54" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="2"/><text x="{x + 55}" y="{y + 31}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="{text}">{name}</text>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 530" style="width:100%;background:#edf5f1;border-radius:8px"><text x="24" y="31" font-family="sans-serif" font-size="18" font-weight="700" fill="#173f40">North-East India | regional context</text><text x="24" y="52" font-family="sans-serif" font-size="12" fill="#607477">Teal = current modelling area · grey = future regional context</text>' + ''.join(shapes) + '<text x="24" y="505" font-family="sans-serif" font-size="12" fill="#607477">State context is geographic orientation only; no future-state observations are implied.</text></svg>'


def overview(data: pd.DataFrame) -> None:
    st.markdown('<div class="hero"><div class="eyebrow">Environmental intelligence platform</div><h1>NE-Hazard Intelligence</h1><p>AI & GIS-Based Multi-Hazard Risk Assessment and Early-Warning System for North-East India</p></div>', unsafe_allow_html=True)
    st.write("A spatial decision workflow for understanding rainfall, terrain, exposure and hazard history before producing flood and landslide intelligence. The current modelling study is Assam + Meghalaya within the wider North-East India vision.")
    metric_row(data)
    st.markdown('<div class="pipeline"><div class="step"><b>01 · DATA SOURCES</b><span>Rainfall, terrain, satellite, hazards, exposure</span></div><div class="arrow">→</div><div class="step"><b>02 · PROCESSING</b><span>Spatial alignment, cleaning, feature preparation</span></div><div class="arrow">→</div><div class="step"><b>03 · EDA</b><span>Patterns, distributions, correlations, spatial analysis</span></div><div class="arrow">→</div><div class="step"><b>04 · AI MODELS</b><span>Classification strategy for flood and landslide</span></div><div class="arrow">→</div><div class="step"><b>05 · EARLY WARNING</b><span>Future risk zones and alert logic</span></div></div>', unsafe_allow_html=True)
    st.subheader("Study geography")
    left, right = st.columns([1.1, 1])
    with left:
        components.html(regional_context_svg(), height=550)
    with right:
        st.markdown('<div class="card"><div class="mini-title">Project region</div><h3>North-East India</h3><p>The complete eight-state region is the long-term project scope.</p><hr><div class="mini-title">Current study area</div><h3>Assam + Meghalaya</h3><p>The teal states are the only states represented in the current real processed grid.</p></div>', unsafe_allow_html=True)


def data_sources(data: pd.DataFrame, availability: dict) -> None:
    st.header("Data & Sources")
    st.write("The project uses source-specific layers that will eventually meet on a common approximately 0.1-degree modelling grid. Statuses below describe the actual current files, not intended downloads.")
    source_cards()
    st.subheader("Current source record")
    table(pd.DataFrame(availability.get("real_sources_used", [])))


def feature_groups(data: pd.DataFrame) -> pd.DataFrame:
    groups = {"Rainfall": ["rain_3h", "rain_24h", "rain_3d", "rain_7d"], "Terrain": ["elevation", "slope", "aspect"], "Satellite": ["NDVI", "NDWI"], "Geographic": ["distance_to_river_km", "distance_to_road_km"], "Exposure": ["population_density"], "Targets": ["flood", "landslide"]}
    rows = []
    for group, fields in groups.items():
        present = [field for field in fields if field in data and data[field].notna().any()]
        rows.append({"feature_group": group, "fields": ", ".join(fields), "populated_fields": len(present), "total_fields": len(fields), "coverage": f"{len(present)}/{len(fields)}"})
    return pd.DataFrame(rows)


def explorer(data: pd.DataFrame) -> None:
    st.header("Dataset Explorer")
    st.markdown('<div class="section-note">A human-readable view of what each data family contributes to the environmental intelligence workflow.</div>', unsafe_allow_html=True)
    metric_row(data)
    a, b = st.columns([1.3, 1])
    with a:
        st.subheader("Actual dataset preview")
        table(data.head(15), 390)
    with b:
        st.subheader("Cells by current state")
        st.bar_chart(data.groupby("region").size().rename("grid_cells"))
        st.caption("These are grid cells, not hazard events.")
    st.subheader("Feature groups and completeness")
    groups = feature_groups(data)
    table(groups)
    st.bar_chart(groups.set_index("feature_group")["populated_fields"])


def preparation(data: pd.DataFrame) -> None:
    st.header("Data Preparation")
    st.write("The preparation workflow converts real state boundary inputs into a common spatial representation. Missing environmental and hazard inputs remain missing; they are never replaced with synthetic values.")
    st.markdown('<div class="pipeline"><div class="step"><b>RAW GEOGRAPHY</b><span>Assam and Meghalaya polygons</span></div><div class="arrow">→</div><div class="step"><b>BOUNDARY FILTER</b><span>Cell centres inside supplied polygons</span></div><div class="arrow">→</div><div class="step"><b>COMMON GRID</b><span>Approximately 0.1-degree cells</span></div><div class="arrow">→</div><div class="step"><b>QUALITY CHECKS</b><span>Stable IDs, coordinates, missingness</span></div><div class="arrow">→</div><div class="step"><b>FEATURE READY</b><span>Source fields retained for later joins</span></div></div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.subheader("Grid output")
        table(data[["cell_id", "region", "latitude", "longitude"]].head(12))
    with right:
        st.subheader("Preparation decisions")
        st.markdown("- Stable `cell_id` for every cell\n- Latitude/longitude retained\n- Source-native precision is not overstated\n- Missing values preserved\n- Future model preparation must avoid temporal leakage")
    st.info("Current master coverage is spatial. There is no event period in the available inputs, so rainfall windows and hazard labels are not attached.")


def exploratory_analysis(data: pd.DataFrame) -> None:
    st.header("Exploratory Analysis")
    st.markdown('<div class="section-note">Explore only variables with actual values. At present, the measured numerical fields are the grid coordinates.</div>', unsafe_allow_html=True)
    load_json(str(EDA_ROOT / "dataset_summary.json"))
    metric_row(data)
    left, right = st.columns(2)
    with left:
        st.subheader("Region distribution")
        st.bar_chart(data.groupby("region").size().rename("grid_cells"))
    with right:
        st.subheader("Available numerical distributions")
        distributions = load_csv(str(EDA_ROOT / "feature_distributions.csv"))
        available = distributions[distributions["count"] > 0]
        if available.empty:
            st.info("No environmental feature distributions are available yet.")
        else:
            st.bar_chart(available.set_index("feature")["mean"])
    tab1, tab2, tab3 = st.tabs(["Completeness", "Correlation", "Spatial EDA"])
    with tab1:
        missing = load_csv(str(EDA_ROOT / "missing_values.csv"))
        st.bar_chart(missing.set_index("column")["missing_percent"])
        st.caption("100% means the field is currently unpopulated; this chart reports data availability, not imputed values.")
    with tab2:
        corr = load_csv(str(EDA_ROOT / "correlations.csv"))
        st.dataframe(corr.style.background_gradient(cmap="YlGnBu", axis=None).format(precision=2), use_container_width=True, height=360)
    with tab3:
        st.write("Spatial EDA of the current modelling grid:")
        st.map(data[["latitude", "longitude"]].rename(columns={"latitude": "lat", "longitude": "lon"}), zoom=6, use_container_width=True)
        svg = EDA_ROOT / "spatial_grid.svg"
        if svg.exists():
            components.html(svg.read_text(encoding="utf-8"), height=500, scrolling=True)


def model_lab() -> None:
    st.header("AI Model Lab")
    st.write("The model strategy is designed for future supervised hazard classification. No model is presented as trained until authoritative event labels are available.")
    cards = [("Logistic Regression", "Interpretable baseline classification model."), ("Random Forest", "Nonlinear relationships and robust tabular modelling."), ("XGBoost", "Gradient-boosted tree candidate for environmental tabular data.")]
    cols = st.columns(3)
    for col, (name, role) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="card"><div class="mini-title">Candidate model</div><h3>{name}</h3><p>{role}</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="pipeline"><div class="step"><b>ENVIRONMENTAL FEATURES</b><span>Rainfall, terrain, exposure, spatial context</span></div><div class="arrow">→</div><div class="step"><b>CLASSIFICATION MODEL</b><span>One task per hazard target</span></div><div class="arrow">→</div><div class="step"><b>FLOOD / LANDSLIDE PROBABILITY</b><span>Future model outputs only</span></div></div>', unsafe_allow_html=True)
    readiness = load_json(str(MODEL_ROOT / "model_readiness.json"))
    st.subheader("Current target readiness")
    table(pd.DataFrame([{"target": target, **status} for target, status in readiness["target_status"].items()]))
    st.warning("Model training is pending because authoritative flood/landslide labels are not currently available.")


def spatial_intelligence(data: pd.DataFrame) -> None:
    st.header("Spatial Intelligence")
    st.write("The map below is a real spatial view of the current grid. It is not a hazard, prediction, risk, or alert map.")
    choice = st.selectbox("Current study area layer", ["All current cells", "Assam", "Meghalaya"])
    view = data if choice == "All current cells" else data[data["region"] == choice]
    st.map(view[["latitude", "longitude"]].rename(columns={"latitude": "lat", "longitude": "lon"}), zoom=6, use_container_width=True)
    with st.expander("Regional context: North-East India", expanded=True):
        components.html(regional_context_svg(), height=550)
    st.caption("Enabled layer: current modelling grid. Rainfall, flood, landslide, terrain, exposure and risk layers are enabled only when populated real fields exist.")


def main() -> None:
    css()
    data = load_csv(str(MASTER_PATH))
    availability = load_json(str(AVAILABILITY_PATH))
    st.sidebar.markdown("<h2 style='color:white;margin-bottom:0'>NE-Hazard<br>Intelligence</h2><p style='color:#b9dfd4'>AI + GIS environmental risk</p>", unsafe_allow_html=True)
    page = st.sidebar.radio("Navigate", ["Overview", "Study Region", "Data & Sources", "Data Preparation", "Exploratory Analysis", "AI Model Lab", "Spatial Intelligence"])
    st.sidebar.divider()
    st.sidebar.caption("Project region: North-East India\n\nCurrent study area: Assam + Meghalaya")
    if page == "Overview":
        overview(data)
    elif page == "Study Region":
        st.header("Study Region")
        st.write("North-East India is the project region. Assam and Meghalaya are the current study area represented in the processed data; the other six states are regional context for future expansion.")
        components.html(regional_context_svg(), height=570)
    elif page == "Data & Sources":
        data_sources(data, availability)
    elif page == "Data Preparation":
        preparation(data)
    elif page == "Exploratory Analysis":
        exploratory_analysis(data)
    elif page == "AI Model Lab":
        model_lab()
    else:
        spatial_intelligence(data)


if __name__ == "__main__":
    main()
