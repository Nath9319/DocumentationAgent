import numpy as np
import pandas as pd
from scipy import stats
import sqlite3
from typing import List, Dict
import scipy.stats as st


class StatsService:

    def _load_data(self, db_path: str, table_name: str, columns=None):
        """
        Load data from SQLite database into a pandas DataFrame.
        If columns is None, load all columns.
        """
        with sqlite3.connect(db_path) as conn:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
        if columns:
            df = df[columns]
        return df

    def perform_ols_regression(self, db_path, table_name, dependent_var, independent_vars):
        """
        Perform OLS regression using numpy's least squares (without statsmodels).
        Returns a summary dictionary with coefficients, intercept, R-squared, and p-values.
        """

        df = self._load_data(db_path, table_name, [dependent_var] + independent_vars)

        # Prepare design matrix X and response vector y
        X = df[independent_vars].values
        y = df[dependent_var].values

        # Add intercept term (column of ones)
        X = np.column_stack((np.ones(X.shape[0]), X))

        # Compute OLS coefficients using least squares
        coef, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)

        # Predicted values and residuals
        y_pred = X @ coef
        residuals = y - y_pred

        # Calculate statistics
        n = len(y)
        p = X.shape[1]  # number of parameters (including intercept)
        dof = n - p
        mse = np.sum(residuals**2) / dof

        # Variance-Covariance Matrix
        XTX_inv = np.linalg.inv(X.T @ X)
        var_b = mse * XTX_inv
        se = np.sqrt(np.diag(var_b))

        # t-statistics for coefficients
        t_stats = coef / se

        # Two-sided p-values
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=dof))

        # R-squared
        ss_total = np.sum((y - np.mean(y))**2)
        ss_residual = np.sum(residuals**2)
        r_squared = 1 - (ss_residual / ss_total)

        # Format results
        summary = {
            "coefficients": dict(zip(['intercept'] + independent_vars, coef)),
            "standard_errors": dict(zip(['intercept'] + independent_vars, se)),
            "t_statistics": dict(zip(['intercept'] + independent_vars, t_stats)),
            "p_values": dict(zip(['intercept'] + independent_vars, p_values)),
            "r_squared": r_squared
        }
        return summary

    def calculate_correlation_matrix(self, db_path, table_name, columns):
        """
        Calculate Pearson correlation matrix for specified columns.
        """
        df = self._load_data(db_path, table_name, columns)
        corr_matrix = df.corr(method='pearson').to_dict()
        return corr_matrix

    def perform_independent_ttest(self, sample1, sample2):
        """
        Perform independent two-sample t-test.
        sample1 and sample2 should be lists or numpy arrays.
        """
        t_stat, p_value = stats.ttest_ind(sample1, sample2, equal_var=False)
        return {
            "t_statistic": t_stat,
            "p_value": p_value
        }
    def calculate_standard_deviation(self, data: list) -> float:
        """
        Calculate the standard deviation of a list of numbers.
        """
        return float(np.std(data))
    
    def calculate_descriptive_stats(self, data: List[float]) -> dict:
        """Calculate descriptive statistics for a list of numbers.
        Returns a dictionary with mean, median, mode, variance, and standard deviation."""
        return {
            "mean": float(np.mean(data)),
            "median": float(np.median(data)),
            "mode": float(stats.mode(data, keepdims=True).mode[0]),
            "variance": float(np.var(data)),
            "std_dev": float(np.std(data)),
        }

    def calculate_z_scores(self, data: List[float]) -> List[float]:
        """Calculate Z-Scores for a list of numbers."""
        return list(((np.array(data) - np.mean(data)) / np.std(data)).round(4))

    

    def calculate_confidence_interval(self, data: List[float], confidence: float) -> dict:
        """Calculate the confidence interval for a list of numbers."""
        n = len(data)
        mean = np.mean(data)
        stderr = st.sem(data)
        margin = stderr * st.t.ppf((1 + confidence) / 2., n-1)
        return {
            "mean": float(mean),
            "confidence_level": confidence,
            "interval": [float(mean - margin), float(mean + margin)]
        }
    


    


# Singleton instance
stats_service = StatsService()
