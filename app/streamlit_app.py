import streamlit as st
import sqlite3
import pandas as pd
import os

# --- DB Setup ---
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "police_checkpost.db")

os.makedirs(DB_DIR, exist_ok=True)
conn = sqlite3.connect(DB_PATH)

# Create table only if not exists
table_check = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='check_post_logs';"
).fetchone()

if not table_check:
    df_csv = pd.read_csv("data/cleaned_traffic_stops.csv")
    df_csv.to_sql("check_post_logs", conn, if_exists="replace", index=False)

# Load data
df = pd.read_sql_query("SELECT * FROM check_post_logs", conn)

# --- UI Setup ---
st.set_page_config(page_title="🚨 SecureCheck Dashboard", layout="wide")
st.title("🚨 SecureCheck - Police Traffic Stop Analytics")

with st.sidebar:
    st.header("🔎 Filters")
    violation_filter = st.selectbox(
        "Violation Type", ["All"] + sorted(df['violation'].dropna().unique())
    )
    gender_filter = st.multiselect(
        "Driver Gender", df['driver_gender'].dropna().unique(), default=None
    )
    day_night_filter = st.radio(
        "Day vs Night", ["All", "Day", "Night"], horizontal=True
    )

# Apply filters
filtered_df = df.copy()

if violation_filter != "All":
    filtered_df = filtered_df[filtered_df['violation'] == violation_filter]
if gender_filter:
    filtered_df = filtered_df[filtered_df['driver_gender'].isin(gender_filter)]
if day_night_filter != "All":
    filtered_df = filtered_df[filtered_df['is_night_stop'].astype(str) == str(day_night_filter == "Night")]

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

# --- Tabs for dashboard sections ---
tab1, tab2, tab3 = st.tabs(["📑 Data Table", "📈 Charts", "🔍 Insights"])

with tab1:
    st.dataframe(filtered_df, use_container_width=True)

with tab2:
    st.subheader("Violation Distribution")
    st.bar_chart(filtered_df['violation'].value_counts())

    st.subheader("Gender Distribution")
    st.bar_chart(filtered_df['driver_gender'].value_counts())

    st.subheader("Day vs Night Stops")
    st.bar_chart(filtered_df['is_night_stop'].value_counts())

with tab3:
    st.subheader("🚦 Quick Insights")
    if filtered_df.empty:
        st.warning("No data available with current filters.")
    else:
        common_violation = filtered_df['violation'].mode()[0]
        arrest_rate = round((filtered_df['is_arrested'].astype(str).value_counts().get("True", 0) / len(filtered_df)) * 100, 2)
        drug_rate = round((filtered_df['drugs_related_stop'].astype(str).value_counts().get("True", 0) / len(filtered_df)) * 100, 2)

        st.write(f"- The **most common violation** is: **{common_violation}**")
        st.write(f"- Overall **arrest rate** is: **{arrest_rate}%**")
        st.write(f"- **Drug-related stops** make up: **{drug_rate}%** of the data")

conn.close()
