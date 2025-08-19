import streamlit as st
import sqlite3
import pandas as pd
import os

# --- DB Setup ---
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "police_checkpost.db")

# Ensure database folder exists
os.makedirs(DB_DIR, exist_ok=True)

# Connect (will create if not exists)
conn = sqlite3.connect(DB_PATH)

# Check if table exists; if not, build from CSV
table_check = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='check_post_logs';"
).fetchone()

if not table_check:
    # Load the CSV and populate table
    df_csv = pd.read_csv("data/cleaned_traffic_stops.csv")
    df_csv.to_sql("check_post_logs", conn, if_exists="replace", index=False)

# --- Streamlit Dashboard ---
st.title("🚨 SecureCheck Dashboard")
st.subheader("Real-time Police Stop Logs")

# Load data from SQLite
df = pd.read_sql_query("SELECT * FROM check_post_logs", conn)

st.dataframe(df)

# --- Filters ---
violation_filter = st.selectbox(
    "Filter by Violation", options=["All"] + sorted(df['violation'].dropna().unique())
)

if violation_filter != "All":
    df = df[df['violation'] == violation_filter]
    st.write(f"Filtered results for: {violation_filter}")
    st.dataframe(df)

# --- KPI Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Stops", df.shape[0])

with col2:
    st.metric("Arrests", df['is_arrested'].astype(str).value_counts().get("True", 0))

with col3:
    st.metric("Drug-related", df['drugs_related_stop'].astype(str).value_counts().get("True", 0))

# Close DB
conn.close()
