import pandas as pd
import numpy as np
import sqlite3
import os
import statsmodels.api as sm
from scipy import stats
from typing import List, Dict, Any, Optional

from app.core.exceptions import DataError

class StatsService:
    """Service for performing statistical analysis."""

    def _get_dataframe_from_sqlite(self, db_path: str, table_name: str) -> pd.DataFrame:
        """Helper to connect to SQLite and get a DataFrame."""
        if not os.path.exists(db_path):
            raise DataError(f"Database file not found at path: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
            conn.close()
            return df
        except Exception as e:
            raise DataError(f"Database error: {e}. Check table name and DB path.")

    def calculate_descriptive_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculates descriptive statistics for a pandas Series."""
        if not pd.api.types.is_numeric_dtype(series):
            raise DataError("Data series must be numeric for statistics.")
        
        stats_dict = series.describe().to_dict()
        stats_dict['median'] = series.median()
        stats_dict['variance'] = series.var()
        stats_dict['skewness'] = series.skew()
        stats_dict['kurtosis'] = series.kurt()
        
        for key, value in stats_dict.items():
            stats_dict[key] = float(value) if pd.notna(value) else None
            
        return stats_dict

    def perform_ols_regression(self, db_path: str, table_name: str, dependent_var: str, independent_vars: List[str]) -> str:
        """Performs Ordinary Least Squares (OLS) regression."""
        df = self._get_dataframe_from_sqlite(db_path, table_name)
        
        all_vars = [dependent_var] + independent_vars
        for var in all_vars:
            if var not in df.columns:
                raise DataError(f"Variable '{var}' not found in table '{table_name}'.")

        y = df[dependent_var]
        X = df[independent_vars]
        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit()
        return str(model.summary())

    def calculate_determinant(self, matrix: List[List[float]]) -> float:
        """Calculates the determinant of a square matrix."""
        np_matrix = np.array(matrix)
        if np_matrix.ndim != 2 or np_matrix.shape[0] != np_matrix.shape[1]:
            raise DataError("Input must be a square matrix.")
        return np.linalg.det(np_matrix)

    def calculate_inverse(self, matrix: List[List[float]]) -> List[List[float]]:
        """Calculates the inverse of a square matrix."""
        np_matrix = np.array(matrix)
        try:
            inverse_matrix = np.linalg.inv(np_matrix)
            return inverse_matrix.tolist()
        except np.linalg.LinAlgError:
            raise DataError("Matrix is singular and cannot be inverted.")
            
    def perform_independent_ttest(self, sample1: List[float], sample2: List[float]) -> Dict[str, float]:
        """Performs an independent two-sample t-test."""
        ttest_result = stats.ttest_ind(sample1, sample2, equal_var=False)
        return {
            "t_statistic": float(ttest_result.statistic),
            "p_value": float(ttest_result.pvalue)
        }

    def calculate_correlation_matrix(self, db_path: str, table_name: str, columns: Optional[List[str]]) -> Dict[str, Any]:
        """Calculates the correlation matrix for specified columns."""
        df = self._get_dataframe_from_sqlite(db_path, table_name)
        
        if columns:
            for col in columns:
                if col not in df.columns:
                    raise DataError(f"Column '{col}' not found in table.")
            data_to_correlate = df[columns]
        else:
            # Use all numeric columns if none are specified
            data_to_correlate = df.select_dtypes(include=np.number)

        if data_to_correlate.shape[1] < 2:
            raise DataError("At least two numeric columns are required for correlation.")

        corr_matrix = data_to_correlate.corr()
        return corr_matrix.to_dict()

# Instantiate the service
stats_service = StatsService()
