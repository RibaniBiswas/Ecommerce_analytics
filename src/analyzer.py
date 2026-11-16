
import pandas as pd


class DataAnalyzer:

    def __init__(self, datasets):

        # Create copies to protect original datasets
        self.datasets = {
            name: df.copy()
            for name, df in datasets.items()
        }

        print("DataAnalyzer initialized successfully!")

    # ==========================================
    # STEP 1: DATA CLEANING
    # ==========================================

    def clean_data(self):

        print("\n========== DATA CLEANING STARTED ==========")

        # Remove duplicate records
        for name, df in self.datasets.items():

            before = len(df)

            df.drop_duplicates(inplace=True)

            after = len(df)

            print(
                f"{name}: Removed {before - after} duplicate rows"
            )

        # Convert order date columns
        order_date_columns = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]

        orders = self.datasets["orders"]

        for column in order_date_columns:

            orders[column] = pd.to_datetime(
                orders[column],
                errors="coerce"
            )

        # Convert review date columns
        review_date_columns = [
            "review_creation_date",
            "review_answer_timestamp"
        ]

        reviews = self.datasets["reviews"]

        for column in review_date_columns:

            reviews[column] = pd.to_datetime(
                reviews[column],
                errors="coerce"
            )

        print("\nDate columns converted successfully!")

        print("\n========== DATA CLEANING COMPLETED ==========")

        return self.datasets

    # ==========================================
    # STEP 2: MISSING VALUE ANALYSIS
    # ==========================================

    def missing_value_analysis(self):

        print("\n========== MISSING VALUE ANALYSIS ==========")

        for name, df in self.datasets.items():

            print(f"\nDataset: {name}")

            missing_values = df.isnull().sum()

            missing_values = missing_values[
                missing_values > 0
            ]

            if missing_values.empty:

                print("No missing values found!")

            else:

                print(missing_values)

                print(
                    "Total missing values:",
                    missing_values.sum()
                )

        print("\n========== ANALYSIS COMPLETED ==========")

    # ==========================================
    # STEP 3: FEATURE ENGINEERING
    # ==========================================

    def create_features(self):

        print("\n========== FEATURE ENGINEERING STARTED ==========")

        orders = self.datasets["orders"]

        # Extract purchase date features
        orders["purchase_year"] = (
            orders["order_purchase_timestamp"].dt.year
        )

        orders["purchase_month"] = (
            orders["order_purchase_timestamp"].dt.month
        )

        orders["purchase_day"] = (
            orders["order_purchase_timestamp"].dt.day
        )

        orders["purchase_hour"] = (
            orders["order_purchase_timestamp"].dt.hour
        )

        orders["purchase_day_name"] = (
            orders["order_purchase_timestamp"].dt.day_name()
        )

        # Calculate delivery duration
        orders["delivery_days"] = (
            orders["order_delivered_customer_date"]
            - orders["order_purchase_timestamp"]
        ).dt.total_seconds() / 86400

        # Calculate delivery delay
        orders["delivery_delay_days"] = (
            orders["order_delivered_customer_date"]
            - orders["order_estimated_delivery_date"]
        ).dt.total_seconds() / 86400

        # Identify late deliveries
        valid_dates = (
            orders["order_delivered_customer_date"].notna()
            & orders["order_estimated_delivery_date"].notna()
        )

        orders["is_late"] = pd.Series(
            pd.NA,
            index=orders.index,
            dtype="boolean"
        )

        orders.loc[valid_dates, "is_late"] = (
            orders.loc[valid_dates, "delivery_delay_days"] > 0
        )

        print("Purchase date features created!")
        print("Delivery features created!")
        print("Late delivery indicator created!")

        print("\n========== FEATURE ENGINEERING COMPLETED ==========")

        return self.datasets

    # ==========================================
    # STEP 4: FEATURE VALIDATION
    # ==========================================

    def validate_features(self):

        print("\n========== FEATURE VALIDATION ==========")

        orders = self.datasets["orders"]

        feature_columns = [
            "purchase_year",
            "purchase_month",
            "purchase_day",
            "purchase_hour",
            "purchase_day_name",
            "delivery_days",
            "delivery_delay_days",
            "is_late"
        ]

        # Display sample records
        print("\nFEATURE SAMPLE:")

        print(
            orders[feature_columns]
            .head(10)
            .to_string(index=False)
        )

        # Check missing values
        print("\nMISSING VALUES IN NEW FEATURES:")

        print(
            orders[feature_columns].isnull().sum()
        )

        # Late delivery distribution
        print("\nLATE DELIVERY DISTRIBUTION:")

        print(
            orders["is_late"].value_counts(dropna=False)
        )

        # Delivery statistics
        print("\nDELIVERY DAYS STATISTICS:")

        print(
            orders["delivery_days"].describe()
        )

        print("\n========== VALIDATION COMPLETED ==========")

        return True
    def create_rfm(self):
            import pandas as pd
    
            orders = self.datasets["orders"].copy()
            payments = self.datasets["payments"].copy()
    
            # Keep delivered orders only
            delivered = orders[
                orders["order_status"] == "delivered"
            ].copy()
    
            # Calculate total customer spending
            customer_spending = (
                delivered[["order_id", "customer_id"]]
                .merge(payments, on="order_id")
                .groupby("customer_id")["payment_value"]
                .sum()
            )
    
            # Calculate RFM metrics
            reference_date = delivered["order_purchase_timestamp"].max()
    
            rfm = delivered.groupby("customer_id").agg(
                Recency=("order_purchase_timestamp",
                         lambda x: (reference_date - x.max()).days),
                Frequency=("order_id", "nunique")
            )
    
            rfm["Monetary"] = customer_spending
    
            rfm = rfm.dropna()
    
            print("\nRFM analysis created successfully!")
            print(rfm.head())
            print("\nRFM dataset shape:", rfm.shape)
    
            return rfm
    def find_optimal_clusters(self, rfm):
            import matplotlib.pyplot as plt
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import KMeans
    
            # Select RFM features
            features = rfm[["Recency", "Frequency", "Monetary"]]
    
            # Scale the features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)
    
            # Calculate inertia for different cluster counts
            inertia = []
    
            for k in range(2, 9):
                model = KMeans(
                    n_clusters=k,
                    random_state=42,
                    n_init=10
                )
                model.fit(scaled_features)
                inertia.append(model.inertia_)
    
            # Plot the Elbow chart
            plt.figure(figsize=(10, 6))
            plt.plot(range(2, 9), inertia, marker="o")
            plt.title("RFM Customer Segmentation - Elbow Method")
            plt.xlabel("Number of Clusters")
            plt.ylabel("Inertia")
            plt.grid(True)
    
            plt.savefig("images/rfm_elbow.png", dpi=300, bbox_inches="tight")
            plt.show()
    
            print("Elbow chart saved to images/rfm_elbow.png")        
    def create_customer_segments(self, rfm, n_clusters=4):
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import KMeans
    
            # Select RFM features
            features = rfm[["Recency", "Frequency", "Monetary"]]
    
            # Scale the features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)
    
            # Train K-Means
            kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10
            )
    
            rfm = rfm.copy()
            rfm["Cluster"] = kmeans.fit_predict(scaled_features)
    
            # Summarize customer segments
            cluster_summary = rfm.groupby("Cluster").agg(
                Customers=("Recency", "count"),
                Avg_Recency=("Recency", "mean"),
                Avg_Frequency=("Frequency", "mean"),
                Avg_Monetary=("Monetary", "mean")
            ).round(2)
    
            print("\nCUSTOMER SEGMENT SUMMARY")
            print(cluster_summary)
    
            return rfm, cluster_summary  
    def label_customer_segments(self, rfm):
            import pandas as pd
    
            rfm = rfm.copy()
    
            # Calculate average RFM values for each cluster
            summary = rfm.groupby("Cluster").agg(
                Avg_Recency=("Recency", "mean"),
                Avg_Frequency=("Frequency", "mean"),
                Avg_Monetary=("Monetary", "mean")
            )
    
            # Rank clusters by their characteristics
            recency_rank = summary["Avg_Recency"].rank(
                ascending=True, method="first"
            )
            frequency_rank = summary["Avg_Frequency"].rank(
                ascending=False, method="first"
            )
            monetary_rank = summary["Avg_Monetary"].rank(
                ascending=False, method="first"
            )
    
            labels = {}
    
            for cluster in summary.index:
                r = recency_rank.loc[cluster]
                f = frequency_rank.loc[cluster]
                m = monetary_rank.loc[cluster]
    
                if r <= 2 and f <= 2 and m <= 2:
                    label = "Champions"
                elif f <= 2:
                    label = "Loyal Customers"
                elif r >= 4 and (f >= 4 or m >= 4):
                    label = "At-Risk Customers"
                elif m <= 2:
                    label = "Big Spenders"
                else:
                    label = "Potential Customers"
    
                labels[cluster] = label
    
            rfm["Segment"] = rfm["Cluster"].map(labels)
    
            print("\nCUSTOMER SEGMENT LABELS")
            print(rfm["Segment"].value_counts())
    
            return rfm             
    
    def visualize_customer_segments(self, rfm):
        import matplotlib.pyplot as plt
        from pathlib import Path

        # Create chart
        plt.figure(figsize=(12, 7))

        scatter = plt.scatter(
            rfm["Recency"],
            rfm["Monetary"],
            c=rfm["Cluster"],
            cmap="viridis",
            s=20,
            alpha=0.6
        )

        plt.title("RFM Customer Segmentation")
        plt.xlabel("Recency (Days)")
        plt.ylabel("Monetary Value")
        plt.colorbar(scatter, label="Customer Cluster")
        plt.grid(alpha=0.2)

        # Save chart in project images folder
        project_dir = Path(__file__).resolve().parent.parent
        image_path = project_dir / "images" / "rfm_customer_segments.png"

        plt.savefig(
            image_path,
            dpi=300,
            bbox_inches="tight"
        )

        print(f"Customer chart saved: {image_path}")

        plt.show()
        plt.close()
