# Documentation for `get_series_from_sqlite`

```python
def get_series_from_sqlite(self, db_path: str, table_name: str, column_name: str) -> pd.Series:
    """
    Retrieves a specified column from a SQLite table and returns it as a pandas Series.

    This function connects to a SQLite database, reads the specified table, and extracts
    the data from the specified column. If the column does not exist in the table, a 
    DataError is raised.

    Parameters:
    ----------
    db_path : str
        The file path to the SQLite database.
    table_name : str
        The name of the table from which to retrieve the column.
    column_name : str
        The name of the column to be extracted from the table.

    Returns:
    -------
    pd.Series
        A pandas Series containing the data from the specified column.

    Raises:
    ------
    DataError
        If the specified column is not found in the table.

    Example:
    --------
    >>> series = get_series_from_sqlite('path/to/database.db', 'my_table', 'my_column')
    >>> print(series)
    """
    df = self.get_dataframe_from_sqlite(db_path, table_name)
    if column_name not in df.columns:
        raise DataError(f"Column '{column_name}' not found in table '{table_name}'.")
    return df[column_name]
``` 

### Documentation Breakdown:
- **Function Purpose:** Clearly states the function's purpose and what it returns.
- **Parameters:** Lists and describes each parameter, including types and purpose.
- **Returns:** Specifies the return type and what it contains.
- **Raises:** Details any exceptions that may be raised, providing clarity on error handling.
- **Example:** Provides a usage example to illustrate how the function can be used in practice.