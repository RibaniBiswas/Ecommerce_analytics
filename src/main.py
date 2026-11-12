
import os
from data_loader import DataLoader

# Get the main project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset folder
DATA_PATH = os.path.join(BASE_DIR, "data", "raw")

# Create DataLoader object
loader = DataLoader(DATA_PATH)

# Load datasets
datasets = loader.load_data()

# Display results
print("\n==============================")
print("ALL DATASETS LOADED SUCCESSFULLY!")
print("==============================")

print("Total datasets:", len(datasets))
