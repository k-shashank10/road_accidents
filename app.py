import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🚦 Road Accident Multi‑Tab Dashboard")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("Road Accident Data.csv")

df = load_data()

# Convert time if available
if "Time" in df.columns:
    df["Hour"] = pd.to_datetime(df["Time"], errors="coerce").dt.hour

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Severity", "Location", "Time of Day", "Weather"])

# --- Tab 1: Severity ---
with tab1:
    st.subheader("Accidents by Severity")
    if "Accident_Severity" in df.columns:
        severity_counts = df["Accident_Severity"].value_counts()
        fig, ax = plt.subplots()
        severity_counts.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_ylabel("Number of Accidents")
        st.pyplot(fig)
    else:
        st.warning("No 'Accident_Severity' column found in dataset.")

# --- Tab 2: Location ---
with tab2:
    st.subheader("Accident Hotspots Map")
    if {"Latitude", "Longitude"}.issubset(df.columns):
        st.map(df[["Latitude", "Longitude"]])
    else:
        st.warning("No latitude/longitude data available.")

# --- Tab 3: Time of Day ---
with tab3:
    st.subheader("Accidents by Hour")
    if "Hour" in df.columns:
        st.line_chart(df["Hour"].value_counts().sort_index())
    else:
        st.warning("No 'Time' column found in dataset.")

# --- Tab 4: Weather ---
with tab4:
    st.subheader("Accidents by Weather Condition")
    if "Weather_Condition" in df.columns:
        weather_counts = df["Weather_Condition"].value_counts().head(10)
        st.bar_chart(weather_counts)
    else:
        st.warning("No 'Weather_Condition' column found in dataset.")
