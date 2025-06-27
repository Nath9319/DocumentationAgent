import pandas as pd
import sqlite3
import os
from fastapi import UploadFile
from io import StringIO
from app.core.exceptions import DataError

class DataService:
    """Service for loading data into pandas objects from files and databases."""

    def get_dataframe_from_sqlite(self, db_path: str, table_name: str) -> pd.DataFrame:
        """
        Connects to a SQLite database and returns an entire table as a pandas DataFrame.
        This function is now used by ValidationService and StatsService.
        """
        if not os.path.exists(db_path):
            raise DataError(f"Database file not found at path: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            # Use pandas read_sql_query for safety and convenience
            query = f'SELECT * FROM "{table_name}"'
            df = pd.read_sql_query(query, conn)
            conn.close()
            if df.empty:
                raise DataError(f"Table '{table_name}' is empty or does not exist.")
            return df
        except Exception as e:
            raise DataError(f"A database error occurred: {e}. Check table and database path.")

    def get_series_from_file(self, file: UploadFile, column_name: str) -> pd.Series:
        """Reads a CSV file, extracts a specified column, and returns it as a pandas Series."""
        if not file.filename.endswith('.csv'):
            raise DataError("Invalid file type. Please upload a CSV file.")
        
        try:
            content = file.file.read().decode("utf-8")
            df = pd.read_csv(StringIO(content))
            
            if column_name not in df.columns:
                raise DataError(f"Column '{column_name}' not found in the CSV file.")
            
            return df[column_name]
        except Exception as e:
            raise DataError(f"Error processing file: {e}")

    def get_series_from_sqlite(self, db_path: str, table_name: str, column_name: str) -> pd.Series:
        """Reads a specific column from a SQLite table and returns it as a pandas Series."""
        df = self.get_dataframe_from_sqlite(db_path, table_name)
        if column_name not in df.columns:
            raise DataError(f"Column '{column_name}' not found in table '{table_name}'.")
        return df[column_name]


# Instantiate the service
data_service = DataService()
