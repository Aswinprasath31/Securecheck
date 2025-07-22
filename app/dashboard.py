import pandas as pd
import streamlit as st

st.set_page_config(page_title="SecureCheck", layout="wide")
st.title("🚨 SecureCheck: Police Check Post Dashboard")

# File uploader
file = st.file_uploader("Upload Cleaned Traffic Stops CSV", type=["csv"])

if file:
    df = pd.read_csv(file)

    # Show dataset preview
    st.subheader("📊 Data Overview")
    st.dataframe(df.head())

    # Filters
    st.subheader("🔍 Filter by Gender and Violation")
    gender = st.selectbox("Driver Gender", options=["All"] + sorted(df['driver_gender'].dropna().unique()))
    violation = st.selectbox("Violation", options=["All"] + sorted(df['violation'].dropna().unique()))

    filtered_df = df.copy()
    if gender != "All":
        filtered_df = filtered_df[filtered_df['driver_gender'] == gender]
    if violation != "All":
        filtered_df = filtered_df[filtered_df['violation'] == violation]

    st.write(f"🔎 Filtered Records: {filtered_df.shape[0]}")
    st.dataframe(filtered_df)

    # Charts
    st.subheader("📈 Violation Frequency")
    st.bar_chart(df['violation'].value_counts())

    st.subheader("🌙 Night vs Day Stops")
    st.bar_chart(df['is_night_stop'].value_counts().rename({1: 'Night', 0: 'Day'}))

    st.subheader("🚹 Gender Distribution")
    st.bar_chart(df['driver_gender'].value_counts())
