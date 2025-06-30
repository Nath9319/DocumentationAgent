# Documentation for `StatsService._load_data`

```python
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
``` 

### Documentation Overview:
- **Purpose:** The `_load_data` method is designed to facilitate the retrieval of data from an SQLite database and load it into a pandas DataFrame for further analysis or processing.
- **Parameters:** The method accepts parameters for the database path, table name, and an optional list of columns to retrieve.
- **Return Value:** It returns a pandas DataFrame containing the queried data.
- **Error Handling:** The docstring specifies potential exceptions that may arise during execution, aiding users in understanding the method's behavior in case of errors.