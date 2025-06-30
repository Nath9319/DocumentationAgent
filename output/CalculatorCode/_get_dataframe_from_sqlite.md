# Documentation for `_get_dataframe_from_sqlite`

```python
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
``` 

### Documentation Breakdown:
- **Function Purpose:** Clearly states the function's role in retrieving data from an SQLite database.
- **Parameters:** Describes the inputs required by the function, including their types and purposes.
- **Returns:** Specifies the output of the function, indicating the type of object returned.
- **Raises:** Lists potential exceptions that the function may raise, providing clarity on error handling.
- **Example:** Provides a practical usage example to illustrate how to call the function.