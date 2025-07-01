import pandas as pd
import sqlite3
import os

# Define the path for the database and CSV file inside the 'calculator_code' folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets the path of the current script
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'sample_database.db')
CSV_PATH = os.path.join(DATA_DIR, 'sample_data.csv')
TABLE_NAME = "housing_data"

def create_sample_database():
    """
    Creates a sample SQLite database from a sample CSV file.
    The script first generates a CSV file with sample housing data,
    then creates a SQLite database and populates a table with that data.
    """
    # Step 1: Clean up old data directory and files if they exist
    if os.path.exists(DATA_DIR):
        print("Removing old 'data' directory and its contents...")
        for filename in os.listdir(DATA_DIR):
            file_path = os.path.join(DATA_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(DATA_DIR)
        print("Old 'data' directory removed.")

    # Ensure the data directory exists again
    os.makedirs(DATA_DIR, exist_ok=True)

    # Step 2: Create a Sample DataFrame and save it as a CSV
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

    # Step 3: Create SQLite Database and Table
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
