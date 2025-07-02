# Documentation for `StatsService._load_data`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### StatsService._load_data(columns: Optional[List[str]] = None) -> pd.DataFrame

**Description:**
The `_load_data` method is responsible for retrieving data from an SQLite database and loading it into a pandas DataFrame. This method allows for flexibility in data retrieval; if the `columns` parameter is not specified (i.e., set to `None`), the method will load all available columns from the database.

**Parameters:**
- `columns` (`Optional[List[str]]`): A list of column names to be retrieved from the database. If set to `None`, all columns will be loaded.

**Expected Input:**
- The `columns` parameter should be a list of strings, where each string corresponds to a column name in the database. If no specific columns are desired, this parameter can be omitted or set to `None`. The method expects that the database connection is properly established and that the specified columns exist in the database schema.

**Returns:**
`pd.DataFrame`: A pandas DataFrame containing the data retrieved from the SQLite database. The DataFrame will include the specified columns if provided; otherwise, it will include all columns.

**Detailed Logic:**
- The method begins by establishing a connection to the SQLite database using the `sqlite3.connect` function, which is part of the external `sqlite3` library.
- It constructs a SQL query to select data from the relevant table. If the `columns` parameter is provided, the query will specify those columns; if it is `None`, the query will use a wildcard to select all columns.
- The method then executes the SQL query using `pd.read_sql_query`, which is part of the external `pandas` library. This function reads the SQL query results directly into a pandas DataFrame.
- Finally, the method returns the populated DataFrame, allowing further data manipulation and analysis within the pandas framework.

---
*Generated with 0% context confidence*
