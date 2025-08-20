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

# If table doesn't exist, load from CSV
table_check = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='check_post_logs';"
).fetchone()

if not table_check:
    try:
        df_csv = pd.read_csv("data/cleaned_traffic_stops.csv")
        df_csv.to_sql("check_post_logs", conn, if_exists="replace", index=False)
    except Exception as e:
        st.error(f"Failed to build database from CSV: {e}")

# Load Full Dataset
df = pd.read_sql_query("SELECT * FROM check_post_logs", conn)

# --- Feature Engineering ---

# Parse dates
if "stop_date" in df.columns:
    df["stop_date"] = pd.to_datetime(df["stop_date"], errors="coerce")

# Derive is_night_stop from stop_time
if "stop_time" in df.columns:
    try:
        hours = pd.to_datetime(df["stop_time"], errors="coerce").dt.hour
        df["is_night_stop"] = hours.apply(
            lambda x: True if pd.notnull(x) and (x >= 20 or x < 6) else False
        )
    except Exception:
        st.warning("⚠️ Couldn't parse stop_time to generate is_night_stop")

# Derived time features
if "stop_date" in df.columns:
    df["stop_day_of_week"] = df["stop_date"].dt.day_name()
    df["is_weekend"] = df["stop_date"].dt.weekday >= 5

# Normalize boolean-like columns
for col in ["is_arrested", "drugs_related_stop", "search_conducted"]:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(
                {
                    "true": True,
                    "false": False,
                    "yes": True,
                    "no": False,
                    "1": True,
                    "0": False,
                }
            )
        )

# --- Dashboard UI ---
st.title("🚨 SecureCheck - Police Traffic Stop Analytics")

# Sidebar Filters
with st.sidebar:
    st.header("🔎 Filters")
    violation_filter = st.selectbox(
        "Violation Type", ["All"] + sorted(df["violation"].dropna().unique())
    )
    gender_filter = st.multiselect(
        "Driver Gender", df["driver_gender"].dropna().unique()
    )
    if "is_night_stop" in df.columns:
        day_night_filter = st.radio(
            "Day vs Night", ["All", "Day", "Night"], horizontal=True
        )
    else:
        day_night_filter = "All"

# --- Apply Filters ---
filtered_df = df.copy()
if violation_filter != "All":
    filtered_df = filtered_df[filtered_df["violation"] == violation_filter]
if gender_filter:
    filtered_df = filtered_df[filtered_df["driver_gender"].isin(gender_filter)]
if day_night_filter != "All" and "is_night_stop" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["is_night_stop"] == (day_night_filter == "Night")
    ]

# --- KPI CARDS ---
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Stops", filtered_df.shape[0])
with col2:
    st.metric("Unique Violations", filtered_df["violation"].nunique())
with col3:
    st.metric(
        "Arrests",
        int(filtered_df["is_arrested"].sum() if "is_arrested" in filtered_df else 0),
    )
with col4:
    st.metric(
        "Drug-related Stops",
        int(
            filtered_df["drugs_related_stop"].sum()
            if "drugs_related_stop" in filtered_df
            else 0
        ),
    )

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📑 Data Table", "📈 Charts", "🔍 Insights"])

# Data Table
with tab1:
    st.subheader("Traffic Stop Records")
    st.dataframe(filtered_df, use_container_width=True)

# Charts
with tab2:
    st.subheader("Visualization of Stops")

    st.markdown("**Violation Distribution**")
    st.bar_chart(filtered_df["violation"].value_counts())

    st.markdown("**Gender Distribution**")
    st.bar_chart(filtered_df["driver_gender"].value_counts())

    if "is_night_stop" in filtered_df.columns:
        st.markdown("**Day vs Night Stops**")
        st.bar_chart(filtered_df["is_night_stop"].value_counts())

    if "stop_date" in filtered_df.columns:
        # Daily trend
        st.markdown("**📅 Stops Over Time (Daily)**")
        ts_daily = (
            filtered_df.groupby(filtered_df["stop_date"].dt.date).size()
        )
        st.line_chart(ts_daily)

        # Monthly trend
        st.markdown("**📅 Stops Over Time (Monthly)**")
        ts_monthly = (
            filtered_df.groupby(filtered_df["stop_date"].dt.to_period("M")).size()
        )
        ts_monthly.index = ts_monthly.index.to_timestamp()
        st.line_chart(ts_monthly)

    if "stop_day_of_week" in filtered_df.columns:
        st.markdown("**📅 Stops by Day of Week**")
        order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        st.bar_chart(
            filtered_df["stop_day_of_week"].value_counts().reindex(order)
        )

    if "is_weekend" in filtered_df.columns:
        st.markdown("**Weekday vs Weekend Stops**")
        st.bar_chart(
            filtered_df["is_weekend"]
            .map({True: "Weekend", False: "Weekday"})
            .value_counts()
        )

# Insights
with tab3:
    st.subheader("🚦 Quick Insights")

    if filtered_df.empty:
        st.warning("No data available with current filters.")
    else:
        # Top violations
        top_violations = (
            filtered_df["violation"].value_counts(normalize=True) * 100
        ).head(3)

        arrest_rate = (
            filtered_df["is_arrested"].mean() * 100
            if "is_arrested" in filtered_df.columns
            else 0
        )
        drug_rate = (
            filtered_df["drugs_related_stop"].mean() * 100
            if "drugs_related_stop" in filtered_df.columns
            else 0
        )

        st.write("### 🔝 Top 3 Violations")
        for i, (violation, pct) in enumerate(top_violations.items(), start=1):
            st.write(f"{i}. **{violation}** ({pct:.2f}%)")

        st.write(f"- Overall **arrest rate** is: **{arrest_rate:.2f}%**")
        st.write(
            f"- **Drug-related stops** make up: **{drug_rate:.2f}%** of the data"
        )

        if "stop_day_of_week" in filtered_df.columns:
            busiest_day = filtered_df["stop_day_of_week"].mode()[0]
            st.write(f"- The **busiest day** for stops is: **{busiest_day}**")
        if "is_weekend" in filtered_df.columns:
            weekend_ratio = filtered_df["is_weekend"].mean() * 100
            st.write(
                f"- **Weekend stops** account for about **{weekend_ratio:.2f}%** of all stops."
            )

# Close DB
conn.close()
