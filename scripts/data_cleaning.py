import pandas as pd

# Load dataset
df = pd.read_excel("../data/traffic_stops.xlsx")

# Step 1: Drop columns with all missing values
df.dropna(axis=1, how='all', inplace=True)

# Step 2: Fill NaN values with defaults or modes
df['driver_gender'].fillna('Unknown', inplace=True)
df['violation'].fillna('Unknown', inplace=True)
df['driver_age'].fillna(df['driver_age'].median(), inplace=True)

# Save cleaned data
df.to_csv("../data/cleaned_traffic_stops.csv", index=False)
print("✅ Cleaned data saved!")
