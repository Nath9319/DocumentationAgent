# Documentation for `StatsService._load_data`

### StatsService._load_data(columns: Optional[List[str]] = None) -> pd.DataFrame

**Description:**
The `_load_data` method is responsible for retrieving data from an SQLite database and loading it into a pandas DataFrame. It provides flexibility in selecting specific columns to load; if no columns are specified, the method will load all available columns from the database.

**Parameters:**
- `columns` (`Optional[List[str]]`): A list of column names to be retrieved from the database. If set to `None`, all columns will be loaded.

**Expected Input:**
- `columns` should be a list of strings representing the names of the columns to be fetched from the database. If no specific columns are required, this parameter can be omitted or set to `None`.

**Returns:**
`pd.DataFrame`: A pandas DataFrame containing the data retrieved from the SQLite database. The structure of the DataFrame will depend on the specified columns or the entire dataset if no columns are specified.

**Detailed Logic:**
- The method initiates a connection to the SQLite database using `sqlite3.connect`, establishing a link to the database file.
- It constructs a SQL query to select data from the database. If the `columns` parameter is provided, the query will specify these columns; otherwise, it will use a wildcard to select all columns.
- The constructed SQL query is executed using `pd.read_sql_query`, which fetches the data and loads it directly into a pandas DataFrame.
- Finally, the method returns the populated DataFrame, allowing further data manipulation and analysis using pandas functionalities.