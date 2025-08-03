import sqlite3
import pandas as pd

# Connect to DB
conn = sqlite3.connect("../database/police_checkpost.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS check_post_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stop_date TEXT,
    stop_time TEXT,
    country_name TEXT,
    driver_gender TEXT,
    driver_age INTEGER,
    driver_race TEXT,
    violation TEXT,
    search_conducted TEXT,
    stop_outcome TEXT,
    is_arrested TEXT,
    stop_duration TEXT,
    drugs_related_stop TEXT
)
""")

# Insert cleaned data
df = pd.read_csv("../data/cleaned_traffic_stops.csv")
df.to_sql('check_post_logs', conn, if_exists='append', index=False)

conn.commit()
conn.close()
print("✅ Database setup and data inserted!")
