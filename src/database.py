
import sqlite3


class DatabaseManager:

    def __init__(self):

        # Create an in-memory SQLite database
        self.connection = sqlite3.connect(":memory:")

        print("SQLite database connected successfully!")

    def load_tables(self, datasets):

        for table_name, dataframe in datasets.items():

            dataframe.to_sql(
                table_name,
                self.connection,
                if_exists="replace",
                index=False
            )

            print(f"Table '{table_name}' created successfully!")

    def close_connection(self):

        self.connection.close()

        print("Database connection closed!")
