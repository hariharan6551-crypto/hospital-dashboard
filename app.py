import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import time
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🏥 Hospital Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------------- DB CONNECTION ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",         
    password="",         
    database="hari"      
)

query = "SELECT * FROM hospitaldata;"
df = pd.read_sql(query, conn)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Controls")
dept_filter = st.sidebar.multiselect("Filter by Department", options=df["Department"].unique(), default=df["Department"].unique())
gender_filter = st.sidebar.multiselect("Filter by Gender", options=df["Gender"].unique(), default=df["Gender"].unique())

df_filtered = df[(df["Department"].isin(dept_filter)) & (df["Gender"].isin(gender_filter))]

# ---------------- KPI CARDS ----------------
st.markdown("## 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_patients = df_filtered["Patient_ID"].nunique()
avg_age = round(df_filtered["Age"].mean(), 1)
male_count = df_filtered[df_filtered["Gender"] == "Male"].shape[0]
female_count = df_filtered[df_filtered["Gender"] == "Female"].shape[0]

for i in range(1, 101, 20):  # simple animated counter
    col1.metric("👨‍⚕️ Total Patients", int(total_patients * (i/100)))
    col2.metric("📊 Avg Age", round(avg_age * (i/100), 1))
    col3.metric("♂️ Male Patients", int(male_count * (i/100)))
    col4.metric("♀️ Female Patients", int(female_count * (i/100)))
    time.sleep(0.05)
st.markdown("---")

# ---------------- CHARTS ----------------
col1, col2 = st.columns(2)

# Chart 1: Line chart - Age Trend by Admission Date
with col1:
    fig1 = px.line(
        df_filtered,
        x="Admission_Date",
        y="Age",
        color="Department",
        markers=True,
        title="📈 Age Trend by Admission Date"
    )
    fig1.update_layout(transition_duration=500)
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Scatter Timeline with Play Slider
with col2:
    fig2 = px.scatter(
        df_filtered,
        x="Admission_Date",
        y="Age",
        size="Age",
        color="Department",
        animation_frame="Admission_Date",
        animation_group="Patient_ID",
        title="🕒 Admissions Over Time (Animated)"
    )
    fig2.update_layout(transition_duration=500)
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- PIE + SUNBURST ----------------
col3, col4 = st.columns(2)

# Pie Chart - Patient Distribution by Department
with col3:
    fig3 = px.pie(
        df_filtered,
        names="Department",
        values="Age",
        hole=0.4,
        title="🧩 Patient Distribution by Department"
    )
    fig3.update_traces(pull=[0.05]*len(df_filtered["Department"].unique()))
    st.plotly_chart(fig3, use_container_width=True)

# Sunburst Chart - Department → Gender
with col4:
    fig4 = px.sunburst(
        df_filtered,
        path=["Department", "Gender"],
        values="Age",
        title="🌞 Department → Gender Breakdown"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- LAST UPDATED + LIVE INDICATOR ----------------
last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
live_icon = "🔴" if int(datetime.now().second) % 2 == 0 else "⚪"

st.markdown(f"### {live_icon} LIVE | ⏰ Last Updated: {last_update}")
st.sidebar.markdown(f"{live_icon} **LIVE**")
st.sidebar.markdown(f"⏰ **Last Updated:** {last_update}")
