# Documentation for `StatsService._load_data`

### StatsService._load_data(columns: Optional[List[str]] = None) -> DataFrame

**Description:**
The `_load_data` method is responsible for loading data from an SQLite database into a Pandas DataFrame. It retrieves all columns from the database unless a specific subset of columns is specified. This method serves as a bridge between the database and the data analysis capabilities of Pandas, facilitating efficient data retrieval for further processing.

**Parameters:**
- `columns` (`Optional[List[str]]`): A list of strings representing the names of the columns to be loaded from the database. If set to `None`, all columns will be loaded.

**Expected Input:**
- `columns` should be a list of valid column names as strings. If no specific columns are required, this parameter can be omitted or set to `None`.

**Returns:**
`DataFrame`: A Pandas DataFrame containing the data retrieved from the SQLite database. The DataFrame will have columns corresponding to the specified column names or all columns if none are specified.

**Detailed Logic:**
- The method begins by establishing a connection to the SQLite database using the `sqlite3.connect` function, which requires the database file name or path.
- It constructs an SQL query to select data from the database. If `columns` is provided, the query will specify those columns; otherwise, it will use a wildcard to select all columns.
- The SQL query is executed using the `pd.read_sql_query` function, which takes the SQL command and the established database connection as parameters.
- The results of the query are returned as a Pandas DataFrame, allowing for easy manipulation and analysis of the data within the broader application context.

---
*Generated with 100% context confidence*
