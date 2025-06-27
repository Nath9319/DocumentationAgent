import sqlite3
import pandas as pd
import os

# Define the path for the database and CSV file
DB_PATH = os.path.join("data", "sample_database.db")
CSV_PATH = os.path.join("data", "sample_data.csv")
TABLE_NAME = "housing_data"

def create_sample_database():
    """
    Creates a sample SQLite database from a sample CSV file.
    The script first generates a CSV file with sample housing data,
    then creates a SQLite database and populates a table with that data.
    """
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)

    # 1. Create a Sample DataFrame and save it as a CSV
    print("Creating sample CSV file...")
    data = {
        'area_sqft': [1500, 2200, 1800, 2500, 1200, 3000, 1600, 2100, 2800, 1900],
        'num_bedrooms': [3, 4, 3, 5, 2, 4, 3, 4, 5, 3],
        'age_years': [10, 5, 8, 2, 15, 7, 12, 6, 3, 9],
        'price_usd': [300000, 450000, 350000, 520000, 250000, 550000, 320000, 430000, 580000, 380000]
    }
    df = pd.DataFrame(data)
    df.to_csv(CSV_PATH, index=False)
    print(f"Sample data saved to {CSV_PATH}")

    # 2. Create SQLite Database and Table
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH}")

    print(f"Creating new SQLite database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        print(f"Successfully created table '{TABLE_NAME}' in the database.")
        
        # Verify
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
        if cursor.fetchone():
            print("Table verification successful.")
        else:
            print("Table verification failed.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    create_sample_database()
