import sqlite3
import pandas as pd

# Load cleaned data
df = pd.read_csv("cleaned_traffic_stops.csv")

# Connect to SQLite (or create it)
conn = sqlite3.connect("securecheck.db")
cursor = conn.cursor()

# Load and execute the table schema
with open("create_tables.sql", "r") as f:
    schema = f.read()
cursor.executescript(schema)
print("✅ Tables created successfully.")

# Insert data into check_post_logs
df.to_sql("check_post_logs", conn, if_exists="append", index=False)
print("✅ Data inserted into check_post_logs.")

# Done
conn.commit()
conn.close()
