import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("../database/police_checkpost.db")

st.title("🚨 SecureCheck Dashboard")
st.subheader("Real-time Police Stop Logs")

df = pd.read_sql_query("SELECT * FROM check_post_logs", conn)

st.dataframe(df)

# Filters
violation_filter = st.selectbox("Filter by Violation", options=["All"] + sorted(df['violation'].unique()))
if violation_filter != "All":
    df = df[df['violation'] == violation_filter]
    st.write(f"Filtered results for: {violation_filter}")
    st.dataframe(df)

# KPI cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Stops", df.shape[0])
with col2:
    st.metric("Arrests", df['is_arrested'].value_counts().get("True", 0))
with col3:
    st.metric("Drug-related", df['drugs_related_stop'].value_counts().get("True", 0))

conn.close()
