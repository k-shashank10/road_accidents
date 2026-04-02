import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🚦 Road Accident Geospatial Dashboard")

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv("Road Accident Data.csv")

df = load_data()

# Preview
st.subheader("Raw Data Preview")
st.write(df.head())

# Sidebar filters
st.sidebar.header("Filters")
if "Year" in df.columns:
    year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique()))
    df = df[df["Year"] == year]

if "Accident_Severity" in df.columns:
    severity = st.sidebar.multiselect("Accident Severity", df["Accident_Severity"].unique(), default=df["Accident_Severity"].unique())
    df = df[df["Accident_Severity"].isin(severity)]

# Accident count by severity
if "Accident_Severity" in df.columns:
    st.subheader("Accidents by Severity")
    severity_counts = df["Accident_Severity"].value_counts()
    fig, ax = plt.subplots()
    severity_counts.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_ylabel("Number of Accidents")
    st.pyplot(fig)

# Geospatial visualization
if {"Latitude", "Longitude"}.issubset(df.columns):
    st.subheader("Accident Hotspots Map")
    st.map(df[["Latitude", "Longitude"]])

# Time of day analysis
if "Time" in df.columns:
    st.subheader("Accidents by Time of Day")
    df["Hour"] = pd.to_datetime(df["Time"], errors="coerce").dt.hour
    st.line_chart(df["Hour"].value_counts().sort_index())
