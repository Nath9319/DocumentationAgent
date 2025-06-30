# Documentation for `StatsService`

```python
class StatsService:
    """
    Service for performing statistical analysis.

    The StatsService class provides methods for retrieving data from an SQLite database, 
    calculating descriptive statistics, performing regression analysis, and computing 
    correlation matrices. It is designed to facilitate various statistical operations 
    on datasets stored in SQLite tables.

    Methods:
    --------
    _get_dataframe_from_sqlite(db_path: str, table_name: str) -> pd.DataFrame:
        Retrieves a DataFrame from a specified SQLite database table.
    
    calculate_descriptive_stats(series: pd.Series) -> Dict[str, Any]:
        Calculates descriptive statistics for a pandas Series.
    
    perform_ols_regression(db_path: str, table_name: str, dependent_var: str, 
                            independent_vars: List[str]) -> str:
        Performs Ordinary Least Squares (OLS) regression on data retrieved from a specified 
        SQLite database table.
    
    calculate_determinant(matrix: List[List[float]]) -> float:
        Calculates the determinant of a square matrix.
    
    calculate_inverse(matrix: List[List[float]]) -> List[List[float]]:
        Calculates the inverse of a square matrix.
    
    perform_independent_ttest(sample1: List[float], sample2: List[float]) -> Dict[str, float]:
        Performs an independent two-sample t-test.
    
    calculate_correlation_matrix(db_path: str, table_name: str, 
                                  columns: Optional[List[str]]) -> Dict[str, Any]:
        Calculates the correlation matrix for specified columns.
    """

    def _get_dataframe_from_sqlite(self, db_path: str, table_name: str) -> pd.DataFrame:
        """
        Retrieve a DataFrame from a specified SQLite database table.

        This function connects to an SQLite database located at the given 
        `db_path`, executes a query to select all records from the specified 
        `table_name`, and returns the results as a pandas DataFrame.

        Parameters:
        ----------
        db_path : str
            The file path to the SQLite database.
        table_name : str
            The name of the table from which to retrieve data.

        Returns:
        -------
        pd.DataFrame
            A DataFrame containing the data from the specified table.

        Raises:
        ------
        DataError
            If the database file does not exist at the specified path, or 
            if there is an error during the database query (e.g., invalid 
            table name or database connection issues).

        Example:
        --------
        df = self._get_dataframe_from_sqlite('path/to/database.db', 'my_table')
        """
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
        """
        Calculates descriptive statistics for a pandas Series.

        This function computes a variety of descriptive statistics for the 
        provided pandas Series, including count, mean, standard deviation, 
        minimum, maximum, quartiles, median, variance, skewness, and kurtosis. 
        The function ensures that the input series is numeric and raises an 
        error if it is not.

        Parameters:
        ----------
        series : pd.Series
            A pandas Series containing numeric data for which descriptive 
            statistics are to be calculated.

        Returns:
        -------
        Dict[str, Any]
            A dictionary containing the calculated descriptive statistics. 
            The keys include:
            - 'count': Number of non-null entries
            - 'mean': Mean of the series
            - 'std': Standard deviation of the series
            - 'min': Minimum value in the series
            - '25%': 25th percentile (first quartile)
            - '50%': Median (second quartile)
            - '75%': 75th percentile (third quartile)
            - 'max': Maximum value in the series
            - 'median': Median of the series
            - 'variance': Variance of the series
            - 'skewness': Skewness of the series
            - 'kurtosis': Kurtosis of the series

        Raises:
        ------
        DataError
            If the input series is not numeric.

        Notes:
        -----
        The function converts all calculated statistics to float, replacing 
        any NaN values with None for better readability in the output.
        """
        if not pd.api.types.is_numeric_dtype(series):
            raise DataError("Data series must be numeric for statistics.")
        
        stats_dict = series.describe().to_dict()
        stats_dict['median'] = series.median()
        stats_dict['