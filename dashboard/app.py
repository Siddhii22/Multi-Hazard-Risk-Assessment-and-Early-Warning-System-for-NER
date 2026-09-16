"""Interactive MSE-1 environmental-intelligence dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "final_dataset_features.csv"
AUDIT_PATH = ROOT / "outputs" / "data_audit" / "audit_summary.json"
PREPROCESSING_PATH = ROOT / "data" / "processed" / "preprocessing_summary.json"
EDA_ROOT = ROOT / "outputs" / "eda"

st.set_page_config(
    page_title="NE Hazard Intelligence",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)


FEATURE_LABELS = {
    "rain_1d_mm": "Rainfall (1 day)",
    "rain_3d_mm": "Rainfall (3 days)",
    "rain_7d_mm": "Rainfall (7 days)",
    "rain_3d_prev_mm": "Previous rainfall (3 days)",
    "rain_7d_prev_mm": "Previous rainfall (7 days)",
    "elevation": "Elevation",
    "slope": "Slope",
    "aspect": "Aspect",
    "TWI": "TWI",
    "SPI": "SPI",
    "ndvi": "NDVI",
    "land_cover_class": "Land-cover class",
    "distance_to_river_km": "Distance to river (km)",
    "distance_to_road_km": "Distance to road (km)",
    "flood_label": "Flood label",
    "landslide_label_static": "Static landslide susceptibility",
}

FEATURE_GROUPS = {
    "Climate": ["rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "rain_3d_prev_mm", "rain_7d_prev_mm"],
    "Terrain": ["elevation", "slope", "aspect", "aspect_sin", "aspect_cos", "TWI", "SPI"],
    "Land surface": ["ndvi", "land_cover_class", "soil_type", "soil_type_code"],
    "Hydrology / infrastructure": ["distance_to_river_km", "distance_to_road_km", "station_count", "interpolation_method"],
    "Exposure": ["population_2011", "households_2011", "literacy_rate_2011", "work_participation_rate_2011"],
    "Hazard labels": ["flood_label", "landslide_label_daily", "landslide_label_static"],
}

SPATIAL_FEATURES = [
    "rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "elevation", "slope", "TWI", "SPI", "ndvi",
    "distance_to_river_km", "distance_to_road_km", "flood_label", "landslide_label_static",
]


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#142f3f; --muted:#526875; --teal:#087f78; --teal-dark:#075b5c; --navy:#102f43; --rust:#a84f2d; --amber:#b66b13; --paper:#eef3f1; --line:#d4e0dc; --card:#ffffff; }
        .stApp { background:var(--paper); color:var(--ink); }
        [data-testid="stSidebar"] { background:var(--navy); border-right:1px solid #274d61; }
        [data-testid="stSidebar"] * { color:#f6faf9 !important; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#c9dbdf !important; }
        [data-testid="stSidebar"] [data-baseweb="radio"] label { border-radius:5px; padding:.5rem .65rem; margin:.12rem 0; color:#eaf4f2 !important; }
        [data-testid="stSidebar"] [data-baseweb="radio"] label:hover { background:#1b4a5a; }
        [data-testid="stSidebar"] [aria-checked="true"] + div { color:#ffffff !important; }
        h1,h2,h3,h4 { color:var(--ink) !important; letter-spacing:0; }
        p, li, label, [data-testid="stCaptionContainer"] { color:var(--ink); }
        [data-testid="stCaptionContainer"] p { color:var(--muted) !important; }
        [data-testid="stMetric"] { background:var(--card); border:1px solid var(--line); border-top:3px solid var(--teal); border-radius:7px; padding:.85rem .95rem; min-height:112px; box-shadow:0 2px 8px rgba(20,47,63,.07); }
        [data-testid="stMetricLabel"] p { color:var(--muted) !important; font-size:.76rem; font-weight:700; line-height:1.2; }
        [data-testid="stMetricValue"] { color:var(--navy) !important; font-size:1.55rem; font-weight:800; }
        [data-testid="stMetricDelta"] { color:var(--muted) !important; }
        .hero { background:#123f4d; border:1px solid #2d6670; color:white; padding:2rem 2.2rem; border-radius:8px; margin-bottom:1.25rem; box-shadow:0 5px 18px rgba(16,47,67,.16); position:relative; overflow:hidden; }
        .hero:after { content:""; position:absolute; right:-5rem; top:-6rem; width:19rem; height:19rem; border:1px solid rgba(188,220,212,.22); border-radius:50%; box-shadow:0 0 0 24px rgba(188,220,212,.06), 0 0 0 48px rgba(188,220,212,.04); }
        .hero h1 { color:white !important; font-size:2.25rem; line-height:1.12; margin:0 0 .5rem; position:relative; z-index:1; }
        .hero p { color:#e2f0ee !important; max-width:850px; margin:0; position:relative; z-index:1; }
        .callout { background:#fff8ee; color:var(--ink); border:1px solid #ead8bf; border-left:4px solid var(--rust); border-radius:5px; padding:.8rem 1rem; margin:.8rem 0 1.2rem; }
        .callout b { color:var(--rust); }
        .flow { display:flex; gap:.45rem; align-items:stretch; margin:1rem 0 1.3rem; }
        .flow-step { flex:1; background:var(--card); color:var(--ink); border:1px solid var(--line); border-top:4px solid var(--teal); border-radius:5px; padding:.8rem; min-height:86px; box-shadow:0 2px 7px rgba(20,47,63,.05); }
        .flow-step strong { display:block; color:var(--navy); font-size:.8rem; }
        .flow-step span { color:var(--muted); font-size:.75rem; }
        .flow-arrow { align-self:center; color:var(--rust); font-size:1.2rem; }
        .section-kicker { color:var(--teal-dark); font-size:.72rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin:.2rem 0 .25rem; }
        .metric-card { background:var(--card); border:1px solid var(--line); border-top:3px solid var(--teal); border-radius:7px; padding:.85rem .95rem; min-height:112px; box-shadow:0 2px 8px rgba(20,47,63,.07); }
        .metric-card .metric-label { color:var(--muted); font-size:.76rem; font-weight:700; line-height:1.25; min-height:2.1em; }
        .metric-card .metric-value { color:var(--navy); font-size:1.55rem; font-weight:800; line-height:1.15; margin:.35rem 0 .15rem; }
        .metric-card .metric-subtitle { color:var(--muted); font-size:.7rem; line-height:1.2; }
        .metric-card.missing { border-top-color:var(--amber); }
        .metric-card.missing .metric-value { color:var(--amber); }
        .warning-panel { background:#fff8ee; border:1px solid #ead8bf; border-left:4px solid var(--amber); color:var(--ink); border-radius:6px; padding:1rem 1.1rem; }
        div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:6px; }
        @media (max-width: 900px) { .flow { flex-direction:column; } .flow-arrow { transform:rotate(90deg); } .hero h1 { font-size:1.75rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner="Loading the processed final dataset...")
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Processed dataset not found: {DATA_PATH}")
    data = pd.read_csv(DATA_PATH, parse_dates=["date"], low_memory=False)
    data["date_only"] = data["date"].dt.date
    return data


@st.cache_data
def load_json(path_string: str) -> dict[str, Any]:
    path = Path(path_string)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def cell_daily_view(data: pd.DataFrame, date_value: str) -> pd.DataFrame:
    view = data[data["date"].dt.strftime("%Y-%m-%d") == date_value].copy()
    return view.sort_values("cell_id")


@st.cache_data
def cell_summary(data: pd.DataFrame) -> pd.DataFrame:
    aggregations = {
        "latitude": ("latitude", "first"),
        "longitude": ("longitude", "first"),
        "date": ("date", "first"),
        "flood_frequency": ("flood_label", "mean"),
        "landslide_susceptibility": ("landslide_label_static", "first"),
    }
    for feature in SPATIAL_FEATURES:
        if feature not in {"flood_label", "landslide_label_static"} and feature in data:
            aggregations[feature] = (feature, "mean")
    return data.groupby("cell_id", as_index=False).agg(**aggregations)


def metric_cards(data: pd.DataFrame) -> None:
    values = [
        ("Observations", f"{len(data):,}", "daily records", False),
        ("Spatial cells", f"{data['cell_id'].nunique():,}", "unique cells", False),
        ("Resolution", "Daily", "temporal resolution", False),
        ("Coverage", f"{data['date'].min():%Y}–{data['date'].max():%Y}", "observation period", False),
        ("Flood-labelled", f"{int(data['flood_label'].sum()):,}", "observed labels", False),
        ("Susceptibility", f"{int(data['landslide_label_static'].sum()):,}", "static observations", False),
    ]
    cards = st.columns(6)
    for card, (label, value, subtitle, missing) in zip(cards, values):
        with card:
            metric_card(label, value, subtitle, missing)


def metric_card(label: str, value: str, subtitle: str, missing: bool = False) -> None:
    modifier = " missing" if missing else ""
    st.markdown(
        f'<div class="metric-card{modifier}"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def flow() -> None:
    st.markdown(
        '<div class="flow">'
        '<div class="flow-step"><strong>01 · INPUTS</strong><span>Environmental, geospatial and exposure data</span></div><div class="flow-arrow">→</div>'
        '<div class="flow-step"><strong>02 · PREPROCESSING</strong><span>Cleaning and feature engineering</span></div><div class="flow-arrow">→</div>'
        '<div class="flow-step"><strong>03 · EDA</strong><span>Spatial, temporal and hazard patterns</span></div><div class="flow-arrow">→</div>'
        '<div class="flow-step"><strong>04 · MODELLING</strong><span>Flood model and susceptibility layer</span></div><div class="flow-arrow">→</div>'
        '<div class="flow-step"><strong>05 · DECISION SUPPORT</strong><span>Future risk interpretation and warning design</span></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def map_chart(data: pd.DataFrame, feature: str, title: str, sample_limit: int = 1200) -> None:
    points = data[["cell_id", "latitude", "longitude", "date", feature]].dropna(subset=["latitude", "longitude", feature]).copy()
    if len(points) > sample_limit:
        points = points.sample(sample_limit, random_state=42)
    points["date"] = points["date"].dt.strftime("%Y-%m-%d")
    chart = px.scatter_map(
        points,
        lat="latitude",
        lon="longitude",
        color=feature,
        hover_name="cell_id",
        hover_data={"latitude": ":.4f", "longitude": ":.4f", "date": True, feature: ":.3f"},
        color_continuous_scale="Tealgrn",
        zoom=5.5,
        height=540,
        title=title,
    )
    chart.update_layout(margin={"r": 0, "t": 48, "l": 0, "b": 0})
    st.plotly_chart(chart, use_container_width=True)


def date_filter(data: pd.DataFrame, key: str) -> tuple[pd.DataFrame, Any, Any]:
    start = data["date"].min().date()
    end = data["date"].max().date()
    selected = st.date_input("Date range", (start, end), min_value=start, max_value=end, key=key)
    if isinstance(selected, tuple) and len(selected) == 2:
        return data[data["date_only"].between(selected[0], selected[1])], selected[0], selected[1]
    return data[data["date_only"] == selected], selected, selected


def overview(data: pd.DataFrame) -> None:
    st.markdown(
        '<div class="hero"><h1>Multi-Hazard Risk Assessment and Early-Warning System</h1>'
        '<p>AI and GIS-based environmental intelligence for Assam + Meghalaya, within the wider North-East India project context.</p></div>',
        unsafe_allow_html=True,
    )
    st.write("The system integrates daily environmental conditions, terrain, hydrology, land-surface characteristics and exposure information to support flood assessment, landslide susceptibility analysis, and future decision support.")
    metric_cards(data)
    st.subheader("Study region")
    st.write("Assam + Meghalaya. The current implementation is an MSE-1 analytical foundation; it does not provide validated real-time operational warnings.")
    map_chart(data.groupby("cell_id", as_index=False).first(), "landslide_label_static", "Spatial study-region coverage")
    st.subheader("Methodology flow")
    flow()
    st.markdown('<div class="callout"><b>Current status:</b> observed labels and susceptibility are available for analysis. Validated flood probabilities and warning statuses are reserved for MSE-2 and later deployment work.</div>', unsafe_allow_html=True)


def study_region(data: pd.DataFrame) -> None:
    st.header("Study Region")
    st.write("Explore actual cell coordinates and selected daily environmental values. Spatial plots are sampled or cell-aggregated so the browser never renders all 522,522 observations.")
    dates = sorted(data["date_only"].unique())
    selected_date = st.selectbox("Date", dates, index=len(dates) - 1, format_func=str)
    daily = cell_daily_view(data, str(selected_date))
    cells = ["All cells"] + sorted(daily["cell_id"].unique().tolist())
    selected_cell = st.selectbox("Cell", cells)
    feature_options = [feature for feature in SPATIAL_FEATURES if feature in daily.columns]
    feature = st.selectbox("Map variable", feature_options, format_func=lambda value: FEATURE_LABELS.get(value, value))
    if selected_cell != "All cells":
        daily = daily[daily["cell_id"] == selected_cell]
    map_chart(daily, feature, f"{FEATURE_LABELS.get(feature, feature)} on {selected_date}")
    if selected_cell != "All cells":
        st.subheader(f"Cell profile: {selected_cell}")
        st.dataframe(daily.drop(columns=["date_only"], errors="ignore").T.rename(columns={daily.index[0]: "value"}), use_container_width=True)


def data_sources(data: pd.DataFrame) -> None:
    st.header("Data & Sources")
    st.write("This inventory describes fields present in the processed final dataset. Source claims are limited to what is documented in the repository.")
    rows = []
    for group, fields in FEATURE_GROUPS.items():
        for field in fields:
            if field not in data.columns:
                continue
            role = "Hazard target" if field.endswith("_label") else "Predictor / context"
            if field in {"population_2011", "households_2011", "literacy_rate_2011", "work_participation_rate_2011"}:
                role = "Exposure / vulnerability context"
            rows.append({"category": group, "feature": field, "data_type": str(data[field].dtype), "missing_percent": round(float(data[field].isna().mean() * 100), 3), "role": role})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=560)
    with st.expander("Documented dataset facts"):
        st.write(f"Rows: {len(data):,}; columns in processed artifact: {len(data.columns)}; cells: {data['cell_id'].nunique():,}; daily coverage: {data['date'].min():%Y-%m-%d} to {data['date'].max():%Y-%m-%d}.")


def data_preparation(data: pd.DataFrame) -> None:
    st.header("Data Preparation")
    audit = load_json(str(AUDIT_PATH))
    preprocessing = load_json(str(PREPROCESSING_PATH))
    a, b, c, d = st.columns(4)
    a.metric("Original rows", f"{audit.get('rows', len(data)):,}")
    b.metric("Original columns", audit.get("columns", 25))
    c.metric("Duplicate rows", audit.get("duplicate_rows", "n/a"))
    d.metric("Duplicate keys", audit.get("duplicate_cell_date_keys", "n/a"))
    st.subheader("Missing-value profile")
    missing = data.drop(columns=["date_only"], errors="ignore").isna().sum().sort_values().rename("missing_count").reset_index()
    missing.columns = ["feature", "missing_count"]
    missing["available_count"] = len(data) - missing["missing_count"]
    chart = px.bar(missing, x="feature", y=["available_count", "missing_count"], title="Available versus missing values", barmode="stack", height=480)
    chart.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(chart, use_container_width=True)
    st.subheader("Implemented flow")
    st.write("Raw Dataset → Date parsing → Duplicate verification → Temporal feature engineering → Rainfall accumulation → Aspect transformation → Missingness indicators → Model-ready dataset")
    engineered = preprocessing.get("feature_engineering", [])
    st.write("Engineered features:", ", ".join(engineered) if engineered else "See preprocessing summary")
    st.info("The raw final CSV remains untouched. No imputation is performed in the processed artifact; modelling imputers are intended to fit training data only.")


def numeric_distribution(data: pd.DataFrame, feature: str, title: str) -> None:
    sample = data[[feature, "flood_label"]].dropna()
    if len(sample) > 50_000:
        sample = sample.sample(50_000, random_state=42)
    st.plotly_chart(px.histogram(sample, x=feature, color="flood_label", marginal="box", title=title, nbins=50), use_container_width=True)


def exploratory_analysis(data: pd.DataFrame) -> None:
    st.header("Exploratory Analysis")
    st.caption("Interactive MSE-1 exploration of the processed final dataset. Charts use filtering and bounded samples where needed.")
    view, _, _ = date_filter(data, "eda_date_range")
    seasons = ["All seasons"] + sorted(data["season"].dropna().unique().tolist())
    season = st.selectbox("Season", seasons)
    if season != "All seasons":
        view = view[view["season"] == season]
    hazard = st.selectbox("Hazard selector", ["Flood label", "Static landslide susceptibility", "Daily landslide label"])
    hazard_column = {"Flood label": "flood_label", "Static landslide susceptibility": "landslide_label_static", "Daily landslide label": "landslide_label_daily"}[hazard]
    feature_choices = [feature for feature in FEATURE_LABELS if feature in view.columns and feature not in {"flood_label", "landslide_label_static"}]
    feature = st.selectbox("Feature selector", feature_choices, format_func=lambda value: FEATURE_LABELS.get(value, value))
    tabs = st.tabs(["Overview", "Rainfall", "Terrain", "Labels", "Spatial"])
    with tabs[0]:
        metric_cards(view)
        st.plotly_chart(px.histogram(view.sample(min(len(view), 40_000), random_state=42), x=feature, color=hazard_column, title=f"{FEATURE_LABELS.get(feature, feature)} by {hazard}"), use_container_width=True)
        st.plotly_chart(px.imshow(view.select_dtypes(include="number").corr(), color_continuous_scale="Tealgrn", aspect="auto", title="Correlation heatmap"), use_container_width=True)
    with tabs[1]:
        for rainfall in ["rain_1d_mm", "rain_3d_mm", "rain_7d_mm"]:
            numeric_distribution(view, rainfall, FEATURE_LABELS[rainfall])
        monthly = view.assign(month=view["date"].dt.month).groupby("month", as_index=False)["rain_1d_mm"].mean()
        st.plotly_chart(px.bar(monthly, x="month", y="rain_1d_mm", title="Monthly mean rainfall"), use_container_width=True)
        seasonal = view.groupby("season", as_index=False)["rain_1d_mm"].mean()
        st.plotly_chart(px.bar(seasonal, x="season", y="rain_1d_mm", title="Seasonal mean rainfall"), use_container_width=True)
    with tabs[2]:
        for terrain in ["elevation", "slope", "TWI", "SPI", "ndvi", "distance_to_river_km", "distance_to_road_km"]:
            numeric_distribution(view, terrain, FEATURE_LABELS.get(terrain, terrain))
    with tabs[3]:
        label_counts = pd.DataFrame({"flood_label": data["flood_label"].value_counts(), "landslide_label_daily": data["landslide_label_daily"].value_counts(), "landslide_label_static": data["landslide_label_static"].value_counts()}).fillna(0).reset_index(names="class")
        st.plotly_chart(px.bar(label_counts, x="class", y=label_counts.columns[1:], barmode="group", title="Flood and landslide label distributions"), use_container_width=True)
        st.plotly_chart(px.scatter(view.sample(min(len(view), 30_000), random_state=42), x="rain_1d_mm", y="flood_label", color="flood_label", title="Rainfall versus flood label", hover_data=["cell_id", "date"]), use_container_width=True)
        st.plotly_chart(px.box(view.sample(min(len(view), 30_000), random_state=42), x="flood_label", y=feature, title=f"{FEATURE_LABELS.get(feature, feature)} versus flood label"), use_container_width=True)
    with tabs[4]:
        summary = cell_summary(view)
        map_chart(summary, "flood_frequency", "Spatial flood frequency", sample_limit=693)
        map_chart(summary, "landslide_susceptibility", "Spatial landslide susceptibility", sample_limit=693)


def hazard_intelligence(data: pd.DataFrame) -> None:
    st.header("Hazard Intelligence")
    st.markdown('<div class="callout"><b>Terminology:</b> flood values are observed labels; static landslide values are susceptibility information; no model predictions are available in MSE-1.</div>', unsafe_allow_html=True)
    flood, landslide = st.tabs(["Flood · observed labels", "Landslide · static susceptibility"])
    with flood:
        st.subheader("Observed flood-labelled observations")
        st.metric("Flood-labelled observations", f"{int(data['flood_label'].sum()):,}")
        flood_data = data[data["flood_label"] == 1]
        context = flood_data[["rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "elevation", "slope", "TWI", "distance_to_river_km"]].describe().T
        st.dataframe(context, use_container_width=True)
        st.plotly_chart(px.scatter(flood_data, x="rain_1d_mm", y="elevation", color="slope", hover_data=["cell_id", "date"], title="Observed flood labels: rainfall and elevation"), use_container_width=True)
        map_chart(cell_summary(data), "flood_frequency", "Observed spatial flood frequency", sample_limit=693)
    with landslide:
        st.subheader("Static landslide susceptibility")
        st.metric("Susceptibility-positive observations", f"{int(data['landslide_label_static'].sum()):,}")
        st.write("This repeated spatial layer is not a daily prediction and is not presented as an operational warning output.")
        subset = data.sample(min(len(data), 30_000), random_state=42)
        st.plotly_chart(px.scatter(subset, x="elevation", y="slope", color="landslide_label_static", size="rain_1d_mm", hover_data=["cell_id", "ndvi", "land_cover_class"], title="Static susceptibility with terrain and rainfall context"), use_container_width=True)
        map_chart(cell_summary(data), "landslide_susceptibility", "Static landslide susceptibility", sample_limit=693)


def ai_model_lab() -> None:
    st.header("AI Model Lab")
    st.info("MSE-1 model identification only. No accuracy, precision, recall, F1, ROC-AUC, PR-AUC, predictions, or alerts are displayed because training has not been performed.")
    models = [
        {"Model": "Logistic Regression", "Purpose": "Interpretable flood baseline", "Why suitable": "Strong transparent baseline for imbalanced tabular data", "Input characteristics": "Scaled numeric and encoded categorical features", "Advantages": "Coefficients are easy to inspect", "Limitations": "Linear decision boundary"},
        {"Model": "Random Forest", "Purpose": "Nonlinear flood candidate", "Why suitable": "Captures interactions among rainfall, terrain and exposure", "Input characteristics": "Mixed tabular environmental features", "Advantages": "Robust nonlinear baseline and feature importance", "Limitations": "Can be biased by spatial dependence and imbalance"},
        {"Model": "XGBoost", "Purpose": "Boosted-tree comparison", "Why suitable": "Often effective for structured tabular relationships", "Input characteristics": "Tabular environmental features", "Advantages": "Flexible nonlinear modelling", "Limitations": "Requires careful tuning and leakage-aware validation"},
    ]
    for model in models:
        with st.expander(model["Model"], expanded=True):
            st.table(pd.DataFrame([model]))
    st.subheader("Current target formulation")
    st.write("Flood → `flood_label` as the primary supervised target. Landslide → `landslide_label_static` as a spatial susceptibility formulation. `landslide_label_daily` is not used as a daily classifier because it has only six positive observations.")
    st.subheader("MSE-2 — Model Training & Evaluation")
    st.write("Model training is planned for MSE-2. Future evaluation will use precision, recall, F1, PR-AUC, ROC-AUC, confusion matrices, false-negative analysis, and spatial-temporal validation.")


def spatial_intelligence(data: pd.DataFrame) -> None:
    st.header("Spatial Intelligence")
    st.write("Select a variable and date to inspect a cell-level interactive map. Hover over points for cell, coordinate, date, and feature values.")
    dates = sorted(data["date_only"].unique())
    selected_date = st.selectbox("Date", dates, index=len(dates) - 1, key="spatial_date")
    feature = st.selectbox("Variable", [feature for feature in SPATIAL_FEATURES if feature in data.columns], format_func=lambda value: FEATURE_LABELS.get(value, value), key="spatial_feature")
    daily = cell_daily_view(data, str(selected_date))
    map_chart(daily, feature, f"{FEATURE_LABELS.get(feature, feature)} · {selected_date}", sample_limit=693)
    selected_cell = st.selectbox("Cell detail", ["None"] + sorted(daily["cell_id"].unique().tolist()), key="spatial_cell")
    if selected_cell != "None":
        st.dataframe(daily[daily["cell_id"] == selected_cell].drop(columns=["date_only"], errors="ignore"), use_container_width=True, hide_index=True)


def early_warning(data: pd.DataFrame) -> None:
    st.header("Early Warning")
    st.markdown('<div class="callout"><b>Non-operational architecture:</b> validated ML warning probability will be connected after MSE-2 model training. No alert is issued here.</div>', unsafe_allow_html=True)
    dates = sorted(data["date_only"].unique())
    selected_date = st.selectbox("Selected date", dates, index=len(dates) - 1, key="warning_date")
    daily = cell_daily_view(data, str(selected_date))
    selected_cell = st.selectbox("Selected cell", sorted(daily["cell_id"].unique().tolist()), key="warning_cell")
    row = daily[daily["cell_id"] == selected_cell].iloc[0]
    st.subheader("Current / selected environmental conditions")
    values = [("Rainfall", "rain_1d_mm", "mm"), ("Previous 3-day accumulation", "rain_3d_prev_mm", "mm"), ("Previous 7-day accumulation", "rain_7d_prev_mm", "mm"), ("Elevation", "elevation", "m"), ("Slope", "slope", "degrees"), ("Distance to river", "distance_to_river_km", "km"), ("Population exposure", "population_2011", "")]
    cards = st.columns(len(values))
    for card, (label, field, unit) in zip(cards, values):
        value = row[field]
        with card:
            if pd.isna(value):
                metric_card(label, "Missing", "not available for selected cell", True)
            else:
                metric_card(label, f"{value:.2f} {unit}".strip(), "selected environmental value")
    st.subheader("Decision-support architecture")
    flow_items = ["Environmental Conditions", "Flood Model", "Hazard Probability", "Exposure + Vulnerability", "Risk Interpretation", "Warning / Decision Support"]
    for index, item in enumerate(flow_items):
        st.markdown(f"**{item}**" + ("  ↓" if index < len(flow_items) - 1 else ""))
    st.info("Validated ML warning probability will be connected after MSE-2 model training. Current values are environmental context only, not predictions or warnings.")


def main() -> None:
    inject_style()
    data = load_data()
    st.sidebar.title("NE Hazard Intelligence")
    st.sidebar.caption("Assam + Meghalaya · MSE-1")
    pages = ["Overview", "Study Region", "Data & Sources", "Data Preparation", "Exploratory Analysis", "Hazard Intelligence", "AI Model Lab", "Spatial Intelligence", "Early Warning"]
    page = st.sidebar.radio("Navigate", pages, key="page")
    st.sidebar.divider()
    st.sidebar.caption("Authoritative processed dataset")
    st.sidebar.caption("Daily observations · 2021–2023")
    handlers = {
        "Overview": overview,
        "Study Region": study_region,
        "Data & Sources": data_sources,
        "Data Preparation": data_preparation,
        "Exploratory Analysis": exploratory_analysis,
        "Hazard Intelligence": hazard_intelligence,
        "AI Model Lab": lambda _: ai_model_lab(),
        "Spatial Intelligence": spatial_intelligence,
        "Early Warning": early_warning,
    }
    handlers[page](data)


if __name__ == "__main__":
    main()
