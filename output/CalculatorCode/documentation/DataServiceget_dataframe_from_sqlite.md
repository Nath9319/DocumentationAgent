# Documentation for `DataService.get_dataframe_from_sqlite`

### DataService.get_dataframe_from_sqlite(database: str, table_name: str) -> pd.DataFrame

**Description:**
The `get_dataframe_from_sqlite` method connects to a specified SQLite database and retrieves an entire table as a Pandas DataFrame. This method is essential for data retrieval and is utilized by both the `ValidationService` and `StatsService` classes within the application.

**Parameters:**
- `database` (`str`): The path to the SQLite database file from which the data will be retrieved.
- `table_name` (`str`): The name of the table within the SQLite database that is to be converted into a DataFrame.

**Expected Input:**
- `database` should be a valid string representing the path to an existing SQLite database file. If the path is incorrect or the database does not exist, an error will occur.
- `table_name` should be a valid string representing the name of an existing table within the specified database. If the table does not exist, an error will be raised.

**Returns:**
`pd.DataFrame`: The method returns a Pandas DataFrame containing all rows and columns from the specified table in the SQLite database. If the table is empty, an empty DataFrame will be returned.

**Detailed Logic:**
- The method begins by establishing a connection to the SQLite database using the `sqlite3.connect` function, passing the `database` parameter.
- It then constructs a SQL query string to select all data from the specified `table_name`.
- The SQL query is executed using the `pd.read_sql_query` function, which takes the constructed SQL query and the established database connection as arguments. This function retrieves the data and formats it into a DataFrame.
- After the data is successfully retrieved, the database connection is closed to free up resources.
- If any errors occur during the connection or data retrieval process, a `DataError` exception is raised, providing a clear indication of the issue encountered. This ensures that the calling code can handle errors gracefully.

---
*Generated with 71% context confidence*
