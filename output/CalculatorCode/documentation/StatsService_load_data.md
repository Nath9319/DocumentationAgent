# Documentation for `StatsService._load_data`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### StatsService._load_data(columns: Optional[List[str]] = None) -> pd.DataFrame

**Description:**
The `_load_data` method retrieves data from an SQLite database and loads it into a pandas DataFrame. If the `columns` parameter is not specified (i.e., set to `None`), the method will load all available columns from the database.

**Parameters:**
- `columns` (`Optional[List[str]]`): A list of column names to be retrieved from the database. If set to `None`, all columns will be loaded.

**Expected Input:**
- The `columns` parameter should be a list of strings, where each string corresponds to a column name in the SQLite database. If no specific columns are desired, this parameter can be omitted or set to `None`.

**Returns:**
`pd.DataFrame`: A pandas DataFrame containing the data retrieved from the SQLite database. The structure of the DataFrame will depend on the specified columns or the entire dataset if no columns are specified.

**Detailed Logic:**
- The method initiates a connection to the SQLite database using the `sqlite3.connect` function.
- It constructs a SQL query to select the desired columns from the database. If `columns` is provided, the query will specify those columns; otherwise, it will select all columns.
- The SQL query is executed using the `pd.read_sql_query` function, which fetches the data and loads it directly into a pandas DataFrame.
- Finally, the method returns the populated DataFrame, allowing further data manipulation and analysis within the application.

---
*Generated with 0% context confidence*
