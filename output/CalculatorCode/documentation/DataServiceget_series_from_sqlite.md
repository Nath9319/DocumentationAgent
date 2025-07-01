# Documentation for `DataService.get_series_from_sqlite`

```markdown
### DataService.get_series_from_sqlite(column_name: str, table_name: str) -> pd.Series

**Description:**  
The `get_series_from_sqlite` method retrieves data from a specified column in a SQLite database table and returns it as a pandas Series. This method is useful for extracting and manipulating data for analysis or further processing within the application.

**Parameters:**
- `column_name` (`str`): The name of the column from which data will be extracted.
- `table_name` (`str`): The name of the SQLite table that contains the specified column.

**Expected Input:**  
- `column_name` should be a valid string representing the column's name in the SQLite table.
- `table_name` should be a valid string representing the table's name in the SQLite database.
- Both parameters must correspond to existing entities in the database; otherwise, a `DataError` will be raised.

**Returns:**  
`pd.Series`: A pandas Series containing the values from the specified column of the table. If the column does not exist or if there are issues with data retrieval, a `DataError` may be raised.

**Detailed Logic:**  
- The method begins by establishing a connection to the SQLite database.
- It constructs a SQL query to select all entries from the specified column of the specified table.
- The query is executed, and the results are fetched.
- If the column is found and data is retrieved successfully, the values are converted into a pandas Series and returned.
- If any issues arise during this process, such as the column or table not existing, a `DataError` is raised with an appropriate message to inform the user of the specific issue encountered.
- This method leverages the capabilities of the pandas library for data manipulation and assumes that the SQLite database is properly configured and accessible.
```