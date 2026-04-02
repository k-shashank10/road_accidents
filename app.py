import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("Road_Accident_Data.csv")
# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Road Accident Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #2e3150;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="metric-container"] label { color: #8892b0 !important; font-size: 13px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e6f1ff !important; font-size: 28px !important; }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #64ffda !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #151722; border-right: 1px solid #2e3150; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: #ccd6f6; }

    /* Section headers */
    .section-header {
        color: #64ffda;
        font-size: 18px;
        font-weight: 600;
        margin: 8px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #2e3150;
    }

    /* Chart containers */
    .chart-container {
        background: #1e2130;
        border: 1px solid #2e3150;
        border-radius: 12px;
        padding: 16px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e2130; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #8892b0; }
    .stTabs [aria-selected="true"] { color: #64ffda !important; }

    h1, h2, h3 { color: #ccd6f6 !important; }
    p, li { color: #8892b0; }

    /* Dividers */
    hr { border-color: #2e3150; }
</style>
""", unsafe_allow_html=True)

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    "fatal":    "#ff6b6b",
    "major":    "#ffa94d",
    "minor":    "#69db7c",
    "primary":  "#64ffda",
    "bg":       "#1e2130",
    "grid":     "#2e3150",
    "text":     "#ccd6f6",
    "subtext":  "#8892b0",
}

SEVERITY_COLORS = {
    "fatal":  "#ff6b6b",
    "major":  "#ffa94d",
    "minor":  "#69db7c",
}

PLOTLY_THEME = dict(
    paper_bgcolor="#1e2130",
    plot_bgcolor="#1e2130",
    font_color="#ccd6f6",
    font_family="Inter, sans-serif",
)

def apply_theme(fig, title="", height=350):
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(text=title, font=dict(color="#64ffda", size=14), x=0.02),
        height=height,
        margin=dict(l=20, r=20, t=45, b=30),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892b0"),
        ),
    )
    fig.update_xaxes(gridcolor="#2e3150", zerolinecolor="#2e3150", title_font_color="#8892b0", tickfont_color="#8892b0")
    fig.update_yaxes(gridcolor="#2e3150", zerolinecolor="#2e3150", title_font_color="#8892b0", tickfont_color="#8892b0")
    return fig

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Road_Accident_Data.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["month_name"] = df["date"].dt.strftime("%b %Y")
    return df

df_raw = load_data()

# ─── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚗 Road Accident\nDashboard")
    st.markdown("---")
    st.markdown("### Filters")

    all_cities   = sorted(df_raw["city"].unique())
    all_severity = sorted(df_raw["accident_severity"].unique())
    all_weather  = sorted(df_raw["weather"].unique())
    all_road     = sorted(df_raw["road_type"].unique())
    all_cause    = sorted(df_raw["cause"].unique())

    sel_city     = st.multiselect("City",             all_cities,   default=all_cities)
    sel_severity = st.multiselect("Severity",         all_severity, default=all_severity)
    sel_weather  = st.multiselect("Weather",          all_weather,  default=all_weather)
    sel_road     = st.multiselect("Road Type",        all_road,     default=all_road)
    sel_cause    = st.multiselect("Accident Cause",   all_cause,    default=all_cause)

    st.markdown("---")
    st.caption("Data: 20,000 accident records across 8 Indian cities")

# ─── Apply Filters ────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["city"].isin(sel_city) &
    df_raw["accident_severity"].isin(sel_severity) &
    df_raw["weather"].isin(sel_weather) &
    df_raw["road_type"].isin(sel_road) &
    df_raw["cause"].isin(sel_cause)
].copy()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🚗 Road Accident Analytics Dashboard")
st.markdown(f"Showing **{len(df):,}** of **{len(df_raw):,}** total accidents | India")
st.markdown("---")

# ─── KPI Row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_accidents  = len(df)
total_casualties = int(df["casualties"].sum())
total_vehicles   = int(df["vehicles_involved"].sum())
fatal_pct        = round(100 * (df["accident_severity"] == "fatal").sum() / max(len(df), 1), 1)
avg_risk         = round(df["risk_score"].mean(), 2)

k1.metric("Total Accidents",    f"{total_accidents:,}")
k2.metric("Total Casualties",   f"{total_casualties:,}")
k3.metric("Vehicles Involved",  f"{total_vehicles:,}")
k4.metric("Fatal Rate",         f"{fatal_pct}%")
k5.metric("Avg Risk Score",     f"{avg_risk}")

st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🗺️ Geographic",
    "⏱️ Time Analysis",
    "🌦️ Conditions",
    "🗺 Map",
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════
with tab1:
    row1_c1, row1_c2 = st.columns(2)

    # Severity donut
    with row1_c1:
        sev_counts = df["accident_severity"].value_counts().reset_index()
        sev_counts.columns = ["severity", "count"]
        fig = px.pie(
            sev_counts, names="severity", values="count",
            color="severity",
            color_discrete_map=SEVERITY_COLORS,
            hole=0.55,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label",
                          textfont_color="#ccd6f6")
        apply_theme(fig, "Accidents by Severity", 350)
        st.plotly_chart(fig, use_container_width=True)

    # Cause bar
    with row1_c2:
        cause_df = df.groupby("cause").agg(
            accidents=("accident_id", "count"),
            casualties=("casualties", "sum"),
        ).reset_index().sort_values("accidents", ascending=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=cause_df["cause"], x=cause_df["accidents"],
            orientation="h", name="Accidents",
            marker_color="#64ffda",
        ))
        fig.add_trace(go.Bar(
            y=cause_df["cause"], x=cause_df["casualties"],
            orientation="h", name="Casualties",
            marker_color="#ff6b6b",
        ))
        fig.update_layout(barmode="group")
        apply_theme(fig, "Accidents & Casualties by Cause", 350)
        st.plotly_chart(fig, use_container_width=True)

    # Severity × Cause heatmap
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        pivot = df.pivot_table(index="cause", columns="accident_severity",
                               values="accident_id", aggfunc="count", fill_value=0)
        fig = px.imshow(
            pivot,
            color_continuous_scale=[[0, "#1e2130"], [0.5, "#4a5568"], [1, "#ff6b6b"]],
            text_auto=True,
            aspect="auto",
        )
        apply_theme(fig, "Cause × Severity Heatmap", 350)
        st.plotly_chart(fig, use_container_width=True)

    # Road type breakdown
    with row2_c2:
        road_sev = df.groupby(["road_type", "accident_severity"]).size().reset_index(name="count")
        fig = px.bar(
            road_sev, x="road_type", y="count", color="accident_severity",
            color_discrete_map=SEVERITY_COLORS, barmode="stack",
        )
        apply_theme(fig, "Accidents by Road Type & Severity", 350)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — GEOGRAPHIC
# ═══════════════════════════════════════════════════════════════════
with tab2:
    city_df = df.groupby("city").agg(
        accidents=("accident_id", "count"),
        casualties=("casualties", "sum"),
        avg_risk=("risk_score", "mean"),
        fatal=("accident_severity", lambda x: (x == "fatal").sum()),
    ).reset_index()
    city_df["fatal_pct"] = round(100 * city_df["fatal"] / city_df["accidents"], 1)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            city_df.sort_values("accidents", ascending=False),
            x="city", y="accidents", color="avg_risk",
            color_continuous_scale=["#69db7c", "#ffa94d", "#ff6b6b"],
            text="accidents",
        )
        fig.update_traces(textposition="outside", textfont_color="#ccd6f6")
        apply_theme(fig, "Total Accidents by City (colored by Avg Risk)", 380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            city_df,
            x="accidents", y="casualties",
            size="avg_risk", color="fatal_pct",
            text="city",
            color_continuous_scale=["#69db7c", "#ffa94d", "#ff6b6b"],
            size_max=40,
        )
        fig.update_traces(textposition="top center", textfont_color="#ccd6f6")
        apply_theme(fig, "Accidents vs Casualties by City", 380)
        st.plotly_chart(fig, use_container_width=True)

    # City state table
    st.markdown("#### City-level Summary")
    display_df = city_df[["city", "accidents", "casualties", "fatal", "fatal_pct", "avg_risk"]].copy()
    display_df.columns = ["City", "Accidents", "Casualties", "Fatal", "Fatal %", "Avg Risk"]
    display_df["Avg Risk"] = display_df["Avg Risk"].round(3)
    display_df = display_df.sort_values("Accidents", ascending=False).reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — TIME ANALYSIS
# ═══════════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    # Hourly trend
    with c1:
        hour_df = df.groupby("hour").agg(
            accidents=("accident_id", "count"),
            casualties=("casualties", "sum"),
        ).reset_index()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=hour_df["hour"], y=hour_df["accidents"],
            name="Accidents", marker_color="#64ffda", opacity=0.75,
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=hour_df["hour"], y=hour_df["casualties"],
            name="Casualties", line=dict(color="#ff6b6b", width=2),
            mode="lines+markers",
        ), secondary_y=True)
        fig.update_xaxes(title_text="Hour of Day", gridcolor="#2e3150")
        fig.update_yaxes(title_text="Accidents", gridcolor="#2e3150", secondary_y=False)
        fig.update_yaxes(title_text="Casualties", gridcolor="#2e3150", secondary_y=True)
        apply_theme(fig, "Accidents & Casualties by Hour", 360)
        st.plotly_chart(fig, use_container_width=True)

    # Day of week
    with c2:
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_df = df.groupby("day_of_week").agg(
            accidents=("accident_id", "count"),
        ).reindex(dow_order).reset_index()

        fig = px.bar(
            dow_df, x="day_of_week", y="accidents",
            color="accidents",
            color_continuous_scale=["#1e2130", "#64ffda"],
            text="accidents",
        )
        fig.update_traces(textposition="outside", textfont_color="#ccd6f6")
        apply_theme(fig, "Accidents by Day of Week", 360)
        st.plotly_chart(fig, use_container_width=True)

    # Monthly trend
    monthly = df.groupby("month").agg(
        accidents=("accident_id", "count"),
        casualties=("casualties", "sum"),
    ).reset_index().sort_values("month")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["accidents"],
        fill="tozeroy", name="Accidents",
        line=dict(color="#64ffda", width=2),
        fillcolor="rgba(100,255,218,0.1)",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["casualties"],
        fill="tozeroy", name="Casualties",
        line=dict(color="#ff6b6b", width=2),
        fillcolor="rgba(255,107,107,0.1)",
    ))
    apply_theme(fig, "Monthly Accident & Casualty Trend", 320)
    st.plotly_chart(fig, use_container_width=True)

    # Peak hour vs off-peak
    c3, c4 = st.columns(2)
    with c3:
        peak_df = df.groupby("is_peak_hour")["accident_id"].count().reset_index()
        peak_df["label"] = peak_df["is_peak_hour"].map({0: "Off-Peak", 1: "Peak Hour"})
        fig = px.pie(peak_df, names="label", values="accident_id",
                     color_discrete_sequence=["#4a5568", "#64ffda"], hole=0.5)
        apply_theme(fig, "Peak vs Off-Peak Accidents", 300)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        we_df = df.groupby("is_weekend")["accident_id"].count().reset_index()
        we_df["label"] = we_df["is_weekend"].map({0: "Weekday", 1: "Weekend"})
        fig = px.pie(we_df, names="label", values="accident_id",
                     color_discrete_sequence=["#4a5568", "#ffa94d"], hole=0.5)
        apply_theme(fig, "Weekday vs Weekend Accidents", 300)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 4 — CONDITIONS
# ═══════════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)

    # Weather
    with c1:
        w_sev = df.groupby(["weather", "accident_severity"]).size().reset_index(name="count")
        fig = px.bar(
            w_sev, x="weather", y="count", color="accident_severity",
            color_discrete_map=SEVERITY_COLORS, barmode="group",
        )
        apply_theme(fig, "Accidents by Weather Condition & Severity", 360)
        st.plotly_chart(fig, use_container_width=True)

    # Visibility
    with c2:
        vis_df = df.groupby(["visibility", "accident_severity"]).size().reset_index(name="count")
        fig = px.bar(
            vis_df, x="visibility", y="count", color="accident_severity",
            color_discrete_map=SEVERITY_COLORS, barmode="stack",
        )
        apply_theme(fig, "Accidents by Visibility & Severity", 360)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    # Traffic density
    with c3:
        td_df = df.groupby("traffic_density").agg(
            accidents=("accident_id", "count"),
            avg_casualties=("casualties", "mean"),
        ).reset_index()
        fig = px.bar(td_df, x="traffic_density", y="accidents",
                     color="avg_casualties",
                     color_continuous_scale=["#69db7c", "#ffa94d", "#ff6b6b"],
                     text="accidents")
        fig.update_traces(textposition="outside", textfont_color="#ccd6f6")
        apply_theme(fig, "Accidents by Traffic Density", 360)
        st.plotly_chart(fig, use_container_width=True)

    # Temperature vs Risk scatter
    with c4:
        sample = df.sample(min(2000, len(df)), random_state=42)
        fig = px.scatter(
            sample, x="temperature", y="risk_score",
            color="accident_severity",
            color_discrete_map=SEVERITY_COLORS,
            opacity=0.5, size_max=5,
        )
        apply_theme(fig, "Temperature vs Risk Score", 360)
        st.plotly_chart(fig, use_container_width=True)

    # Lanes analysis
    lane_df = df.groupby("lanes").agg(
        accidents=("accident_id", "count"),
        casualties=("casualties", "sum"),
        avg_risk=("risk_score", "mean"),
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=lane_df["lanes"], y=lane_df["accidents"],
        name="Accidents", marker_color="#64ffda", opacity=0.75,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=lane_df["lanes"], y=lane_df["avg_risk"],
        name="Avg Risk", line=dict(color="#ffa94d", width=2),
        mode="lines+markers",
    ), secondary_y=True)
    fig.update_xaxes(title_text="Number of Lanes", gridcolor="#2e3150")
    apply_theme(fig, "Accidents & Avg Risk by Number of Lanes", 320)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 5 — MAP
# ═══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### Accident Locations Map")
    st.caption("Showing a sample of accident locations colored by severity.")

    sample_map = df.sample(min(3000, len(df)), random_state=42)
    fig = px.scatter_mapbox(
        sample_map,
        lat="latitude", lon="longitude",
        color="accident_severity",
        color_discrete_map=SEVERITY_COLORS,
        size="risk_score",
        size_max=10,
        opacity=0.65,
        hover_data=["city", "cause", "casualties", "risk_score"],
        zoom=4,
        center={"lat": 20.5, "lon": 79.0},
        mapbox_style="carto-darkmatter",
        height=600,
    )
    apply_theme(fig, "", 620)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # City cluster bar
    st.markdown("#### Accident Density by City")
    city_coords = df.groupby("city").agg(
        accidents=("accident_id", "count"),
        lat=("latitude", "mean"),
        lon=("longitude", "mean"),
    ).reset_index()

    fig2 = px.scatter_mapbox(
        city_coords,
        lat="lat", lon="lon",
        size="accidents",
        color="accidents",
        color_continuous_scale=["#64ffda", "#ffa94d", "#ff6b6b"],
        size_max=50,
        text="city",
        zoom=4,
        center={"lat": 20.5, "lon": 79.0},
        mapbox_style="carto-darkmatter",
        hover_data=["city", "accidents"],
        height=500,
    )
    apply_theme(fig2, "", 520)
    fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig2, use_container_width=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Road Accident Analytics Dashboard · Built with Streamlit & Plotly · Data: 20,000 records across 8 Indian cities")
