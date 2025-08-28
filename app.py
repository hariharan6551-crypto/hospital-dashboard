import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
import time
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🏥 Hospital Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------------- DB CONNECTION ----------------
def get_connection():
    try:
        conn = pymysql.connect(
            host="sql111.infinityfree.com",  # InfinityFree host
            user="if0_39806258",             # Your InfinityFree DB username
            password="YOUR_PASSWORD",       # Replace with your InfinityFree DB password
            database="if0_39806258_hospital_db",  # Your InfinityFree DB name
            port=3306
        )
        st.sidebar.success("✅ Database connected successfully!")
        return conn
    except Exception as e:
        st.sidebar.error(f"❌ Database connection failed: {e}")
        return None

conn = get_connection()

# ---------------- FETCH DATA ----------------
if conn:
    query = "SELECT * FROM hospitaldata;"  # Make sure this table exists
    df = pd.read_sql(query, conn)
    conn.close()
else:
    st.error("Database connection failed. Please check your credentials.")
    st.stop()

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

with col1:
    fig1 = px.line(
        df_filtered,
        x="Admission_Date",
        y="Age",
        color="Department",
        markers=True,
        title="📈 Age Trend by Admission Date"
    )
    st.plotly_chart(fig1, use_container_width=True)

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
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig3 = px.pie(
        df_filtered,
        names="Department",
