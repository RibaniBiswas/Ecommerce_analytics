
import os
from pathlib import Path
import pandas as pd

from src.data_loader import DataLoader
from src.database import DatabaseManager
from src.analyzer import DataAnalyzer


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "raw"
SQL_PATH = BASE_DIR / "sql" / "queries.sql"
OUTPUT_PATH = BASE_DIR / "data"
IMAGE_PATH = BASE_DIR / "images"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
IMAGE_PATH.mkdir(parents=True, exist_ok=True)


def main():

    print("\n======================================")
    print("   E-COMMERCE ANALYTICS PROJECT")
    print("======================================")

    # ======================================
    # 2. LOAD DATASETS
    # ======================================

    print("\nSTEP 1: Loading datasets...", flush=True)

    loader = DataLoader(str(DATA_PATH))
    datasets = loader.load_data()

    print("\nAll datasets loaded successfully!", flush=True)

    # ======================================
    # 3. DATA CLEANING
    # ======================================

    print("\nSTEP 2: Cleaning datasets...", flush=True)

    analyzer = DataAnalyzer(datasets)

    cleaned_datasets = analyzer.clean_data()

    print("\nData cleaning completed!", flush=True)

    # ======================================
    # 4. MISSING VALUE ANALYSIS
    # ======================================

    print("\nSTEP 3: Missing value analysis...", flush=True)

    analyzer.missing_value_analysis()

    # ======================================
    # 5. FEATURE ENGINEERING
    # ======================================

    print("\nSTEP 4: Creating features...", flush=True)

    analyzer.create_features()

    analyzer.validate_features()

    print("\nFeature engineering completed!", flush=True)

    # ======================================
    # 6. SQL DATABASE
    # ======================================

    print("\nSTEP 5: Connecting SQLite database...", flush=True)

    db = DatabaseManager()

    try:
        db.load_tables(cleaned_datasets)

        print("\nSQL database tables created!", flush=True)

        # Execute SQL queries
        if SQL_PATH.exists():

            print("\nSTEP 6: Running SQL queries...", flush=True)

            sql_content = SQL_PATH.read_text(encoding="utf-8")

            queries = [
                query.strip()
                for query in sql_content.split(";")
                if query.strip()
            ]

            for index, query in enumerate(queries, start=1):

                print(f"\nSQL QUERY {index}", flush=True)

                try:
                    result = pd.read_sql_query(
                        query,
                        db.connection
                    )

                    print(result.to_string(index=False))

                except Exception as error:
                    print(f"SQL query {index} failed: {error}")

        else:
            print("SQL queries file not found!")

    finally:
        db.close_connection()

    # ======================================
    # 7. RFM CUSTOMER ANALYSIS
    # ======================================

    print("\nSTEP 7: Creating RFM analysis...", flush=True)

    rfm = analyzer.create_rfm()

    print("\nTotal customers analyzed:", len(rfm))

    # ======================================
    # 8. ELBOW METHOD
    # ======================================

    print("\nSTEP 8: Finding optimal clusters...", flush=True)

    analyzer.find_optimal_clusters(rfm)

    print("\nElbow Method completed!", flush=True)

    # ======================================
    # 9. K-MEANS CUSTOMER SEGMENTATION
    # ======================================

    print("\nSTEP 9: Training K-Means model...", flush=True)

    rfm, cluster_summary = analyzer.create_customer_segments(
        rfm,
        n_clusters=5
    )

    print("\nK-Means clustering completed!", flush=True)

    # ======================================
    # 10. CUSTOMER SEGMENT LABELS
    # ======================================

    print("\nSTEP 10: Assigning customer labels...", flush=True)

    rfm = analyzer.label_customer_segments(rfm)

    print("\nCustomer labels assigned!", flush=True)

    # ======================================
    # 11. CUSTOMER SEGMENT VISUALIZATION
    # ======================================

    print("\nSTEP 11: Creating customer visualization...", flush=True)

    analyzer.visualize_customer_segments(rfm)

    print("\nCustomer visualization completed!", flush=True)

    # ======================================
    # 12. EXPORT CUSTOMER SEGMENTS
    # ======================================

    print("\nSTEP 12: Exporting customer data...", flush=True)

    rfm.to_csv(
        OUTPUT_PATH / "customer_segments.csv",
        index=True
    )

    cluster_summary.to_csv(
        OUTPUT_PATH / "cluster_summary.csv"
    )

    print("\nCustomer segmentation files exported!")

    print("Saved: data/customer_segments.csv")
    print("Saved: data/cluster_summary.csv")

    # ======================================
    # 13. FINAL SUMMARY
    # ======================================

    print("\n========== CUSTOMER SEGMENT SUMMARY ==========")

    print(cluster_summary.to_string())

    print("\nCustomer counts by segment:")

    print(rfm["Segment"].value_counts())

    print("\nTotal customers:", len(rfm))
    print("Number of clusters:", rfm["Cluster"].nunique())

    print("\n======================================")
    print("   PROJECT EXECUTION COMPLETED!")
    print("======================================")


# ==========================================
# MAIN ENTRY POINT
# ==========================================


if __name__ == "__main__":

    datasets = load_data()

    prepared_data = prepare_data(datasets)

    kpis = calculate_kpis(prepared_data)

    print("\nOLIST KPI SUMMARY")

    for name, value in kpis.items():
        print(f"{name}: {value:,.2f}")

    export_kpi_dashboard(kpis)

    print("\nStep 3 completed successfully!")

