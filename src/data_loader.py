import pandas as pd 
import os

class DataLoader:

    def __init__(self, data_path):

        self.data_path = data_path

        self.datasets = {}

        print("DataLoader initialized successfully!")
    
    def load_data(self):

        file_names = {
            "orders": "olist_orders_dataset.csv",
            "order_items": "olist_order_items_dataset.csv",
            "customers": "olist_customers_dataset.csv",
            "payments": "olist_order_payments_dataset.csv",
            "reviews": "olist_order_reviews_dataset.csv",
            "products": "olist_products_dataset.csv",
            "sellers": "olist_sellers_dataset.csv",
            "geolocation": "olist_geolocation_dataset.csv",
            "category_translation": "product_category_name_translation.csv"
        }

        for name, file_name in file_names.items():

            file_path = os.path.join(self.data_path, file_name)

            self.datasets[name] = pd.read_csv(file_path)

            print(f"{name} loaded successfully!")

        return self.datasets

