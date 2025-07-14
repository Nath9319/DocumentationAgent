# Documentation for `DataService.get_dataframe_from_sqlite`

### DataService.get_dataframe_from_sqlite(database: str) -> DataFrame

**Description:**
The `get_dataframe_from_sqlite` method connects to a specified SQLite database and retrieves an entire table as a Pandas DataFrame. This function is essential for data retrieval tasks within the application, allowing other services, such as `ValidationService` and `StatsService`, to access data stored in SQLite format.

**Parameters:**
- `database` (`str`): The path to the SQLite database file from which the data will be retrieved.

**Expected Input:**
- `database` must be a valid string representing the path to an existing SQLite database file. If the specified database does not exist, the function may raise an error.

**Returns:**
`DataFrame`: A Pandas DataFrame containing all rows and columns from the specified table in the SQLite database.

**Detailed Logic:**
- The method begins by establishing a connection to the SQLite database using the `sqlite3.connect` function, passing the `database` parameter.
- It then executes a SQL query to select all data from the desired table using the `pd.read_sql_query` function, which takes the SQL query string and the established connection as arguments.
- After retrieving the data, the method checks if the resulting DataFrame is empty. If it is, it raises a `DataError` to indicate that no data was found in the specified table.
- Finally, the method ensures that the database connection is properly closed using `conn.close()`, releasing any resources associated with the connection.
- This function encapsulates the entire process of connecting to the database, executing the query, and returning the results as a DataFrame, making it a critical utility for data handling in the application.

---
*Generated with 71% context confidence*
