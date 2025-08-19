import streamlit as st
import sqlite3
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚨 SecureCheck Dashboard", layout="wide")

# --- DB Setup ---
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "police_checkpost.db")

os.makedirs(DB_DIR, exist_ok=True)
conn = sqlite3.connect(DB_PATH)

# Check if table exists; if not, load from CSV
table_check = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='check_post_logs';"
).fetchone()

if not table_check:
    try:
        df_csv = pd.read_csv("data/cleaned_traffic_stops.csv")
        df_csv.to_sql("check_post_logs", conn, if_exists="replace", index=False)
    except Exception as e:
        st.error(f"Failed to build database from CSV: {e}")

# Load data from DB
df = pd.read_sql_query("SELECT * FROM check_post_logs", conn)

# --- Feature Engineering: Add is_night_stop ---
if "stop_time" in df.columns:
    try:
        df["stop_time"] = pd.to_datetime(df["stop_time"], errors="coerce").dt.time
        hours = pd.to_datetime(df["stop_time"].astype(str), errors="coerce").dt.hour
        df["is_night_stop"] = hours.apply(lambda x: True if pd.notnull(x) and (x >= 20 or x < 6) else False)
    except Exception as e:
        st.warning(f"⚠️ Couldn't process stop_time to create is_night_stop: {e}")

# --- Dashboard UI ---
st.title("🚨 SecureCheck - Police Traffic Stop Analytics")

# Sidebar Filters
with st.sidebar:
    st.header("🔎 Filters")
    violation_filter = st.selectbox("Violation Type", ["All"] + sorted(df['violation'].dropna().unique()))
    gender_filter = st.multiselect("Driver Gender", df['driver_gender'].dropna().unique())
    if "is_night_stop" in df.columns:
        day_night_filter = st.radio("Day vs Night", ["All", "Day", "Night"], horizontal=True)
    else:
        day_night_filter = "All"

# Apply Filters
filtered_df = df.copy()

if violation_filter != "All":
    filtered_df = filtered_df[filtered_df['violation'] == violation_filter]

if gender_filter:
    filtered_df = filtered_df[filtered_df['driver_gender'].isin(gender_filter)]

if day_night_filter != "All" and "is_night_stop" in filtered_df.columns:
    if day_night_filter == "Night":
        filtered_df = filtered_df[filtered_df['is_night_stop'] == True]
    else:
        filtered_df = filtered_df[filtered_df['is_night_stop'] == False]

# --- KPI Cards ---
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Stops", filtered_df.shape[0])

with col2:
    st.metric("Unique Violations", filtered_df['violation'].nunique())

with col3:
    st.metric("Arrests", filtered_df['is_arrested'].astype(str).value_counts().get("True", 0))

with col4:
    st.metric("Drug-related Stops", filtered_df['drugs_related_stop'].astype(str).value_counts().get("True", 0))

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📑 Data Table", "📈 Charts", "🔍 Insights"])

# Table View
with tab1:
    st.subheader("Traffic Stop Records")
    st.dataframe(filtered_df, use_container_width=True)

# Charts View
with tab2:
    st.subheader("Visualization of Stops")
    st.markdown("**Violation Distribution**")
    st.bar_chart(filtered_df['violation'].value_counts())

    st.markdown("**Gender Distribution**")
    st.bar_chart(filtered_df['driver_gender'].value_counts())

    # Day vs Night
    if "is_night_stop" in filtered_df.columns:
        st.markdown("**Day vs Night Stops**")
        st.bar_chart(filtered_df['is_night_stop'].value_counts())

    # Time-series by stop_date
    if "stop_date" in filtered_df.columns:
        st.markdown("**📅 Stops Over Time**")
        ts_df = filtered_df.copy()
        ts_df["stop_date"] = pd.to_datetime(ts_df["stop_date"], errors="coerce")
        ts_summary = ts_df.groupby(ts_df["stop_date"].dt.date).size()
        st.line_chart(ts_summary)

# Insights View
with tab3:
    st.subheader("🚦 Quick Insights")
    if filtered_df.empty:
        st.warning("No data available with current filters.")
    else:
        common_violation = filtered_df['violation'].mode()[0]
        arrest_rate = round(
            (filtered_df['is_arrested'].astype(str).value_counts().get("True", 0) / len(filtered_df)) * 100,
            2,
        )
        drug_rate = round(
            (filtered_df['drugs_related_stop'].astype(str).value_counts().get("True", 0) / len(filtered_df)) * 100,
            2,
        )

        st.write(f"- The **most common violation** is: **{common_violation}**")
        st.write(f"- Overall **arrest rate** is: **{arrest_rate}%**")
        st.write(f"- **Drug-related stops** make up: **{drug_rate}%** of the data")

# Close DB
conn.close()
