


import os
from src.data_loader import DataLoader
from src.database import DatabaseManager
import pandas as pd

# Get the actual project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the correct dataset path
DATA_PATH = os.path.join(BASE_DIR, "data", "raw")

print("Project directory:", BASE_DIR)
print("Dataset directory:", DATA_PATH)


# Initialize DataLoader
loader = DataLoader(DATA_PATH)

# Load all datasets
datasets = loader.load_data()
loader.inspect_data()

# Create SQLite database
db = DatabaseManager()

# Load all datasets into SQLite
db.load_tables(datasets)

# Execute SQL Query 01

sql_path = os.path.join(BASE_DIR, "sql", "queries.sql")

with open(sql_path, "r", encoding="utf-8") as file:
    query = file.read()

result = pd.read_sql_query(query, db.connection)

print("\nMONTHLY REVENUE ANALYSIS")
print(result.to_string(index=False))



# Display results
print("\n================================")
print("ALL DATASETS LOADED SUCCESSFULLY!")
print("================================")

print("Total datasets:", len(datasets))
