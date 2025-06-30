# Documentation for `StatsService`

```python
class StatsService:
    """
    StatsService provides various statistical analysis methods for datasets 
    stored in an SQLite database or in-memory lists. It includes functionalities 
    for loading data, performing regression analysis, calculating correlation 
    matrices, conducting t-tests, and computing descriptive statistics.

    Methods:
    --------
    _load_data(db_path: str, table_name: str, columns=None) -> pandas.DataFrame:
        Load data from an SQLite database into a pandas DataFrame.

    perform_ols_regression(db_path: str, table_name: str, dependent_var: str, independent_vars: list) -> dict:
        Perform Ordinary Least Squares (OLS) regression and return a summary of results.

    calculate_correlation_matrix(db_path: str, table_name: str, columns: list) -> dict:
        Calculate the Pearson correlation matrix for specified columns in a database table.

    perform_independent_ttest(sample1: list, sample2: list) -> dict:
        Perform an independent two-sample t-test and return the t-statistic and p-value.

    calculate_standard_deviation(data: list) -> float:
        Calculate the standard deviation of a list of numbers.

    calculate_descriptive_stats(data: List[float]) -> dict:
        Calculate descriptive statistics for a list of numbers.

    calculate_z_scores(data: List[float]) -> List[float]:
        Calculate Z-Scores for a list of numbers.

    calculate_confidence_interval(data: List[float], confidence: float) -> dict:
        Calculate the confidence interval for a list of numbers.
    """

    def _load_data(self, db_path: str, table_name: str, columns=None):
        """
        Load data from an SQLite database into a pandas DataFrame.

        This method connects to the specified SQLite database and retrieves data 
        from the given table. If the `columns` parameter is not provided (i.e., 
        it is None), all columns from the table will be loaded into the DataFrame. 
        If specific columns are specified, only those columns will be included in 
        the resulting DataFrame.

        Parameters:
        ----------
        db_path : str
            The file path to the SQLite database from which to load data.
        
        table_name : str
            The name of the table in the database to query data from.
        
        columns : list, optional
            A list of column names to load from the table. If None, all columns 
            will be loaded. Default is None.

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing the data retrieved from the specified table 
            in the SQLite database.

        Raises:
        ------
        sqlite3.Error
            If there is an error connecting to the database or executing the query.
        KeyError
            If any specified columns do not exist in the DataFrame.
        """
        with sqlite3.connect(db_path) as conn:
            query = f'SELECT * FROM {table_name}'
            df = pd.read_sql_query(query, conn)
        if columns:
            df = df[columns]
        return df

    def perform_ols_regression(self, db_path: str, table_name: str, dependent_var: str, independent_vars: list) -> dict:
        """
        Perform Ordinary Least Squares (OLS) regression using NumPy's least squares method.

        This method loads data from a specified database table, performs OLS regression on the 
        provided dependent and independent variables, and returns a summary of the regression results.

        Parameters:
        ----------
        db_path : str
            The file path to the database from which to load the data.
        
        table_name : str
            The name of the table in the database containing the data.
        
        dependent_var : str
            The name of the dependent variable (the outcome variable).
        
        independent_vars : list of str
            A list of names of the independent variables (predictor variables).

        Returns:
        -------
        dict
            A dictionary containing the following keys:
            - 'coefficients': A dictionary mapping variable names to their estimated coefficients.
            - 'standard_errors': A dictionary mapping variable names to their estimated standard errors.
            - 't_statistics': A dictionary mapping variable names to their t-statistics.
            - 'p_values': A dictionary mapping variable names to their p-values.
            - 'r_squared': The R-squared value of the regression model, indicating the proportion of variance explained by the model.

        Notes:
        -----
        This implementation does not use the `statsmodels` library and relies solely on NumPy for calculations.
        Ensure that the database and table specified contain the necessary columns for the dependent and independent variables.
        """
        df = self._load_data(db_path, table_name, [dependent_var] + independent_vars)
        X = df[independent_vars].values
        y = df[dependent_var].values
        X = np.column_stack((np.ones(X.shape[0]), X))
        coef,