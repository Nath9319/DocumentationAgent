# Documentation for `StatsService._load_data`

### StatsService._load_data(columns: Optional[List[str]] = None) -> pandas.DataFrame

**Description:**
The `_load_data` method is responsible for loading data from a SQLite database into a Pandas DataFrame. It utilizes the `data_service.get_dataframe_from_sqlite` function to execute a SQL query and retrieve the data. If the `columns` parameter is not specified (i.e., it is `None`), the method will load all available columns from the database.

**Parameters:**
- `columns` (`Optional[List[str]]`): A list of column names to be retrieved from the database. If set to `None`, all columns will be loaded.

**Expected Input:**
- `columns` can either be a list of strings representing the specific column names to be fetched or `None` to indicate that all columns should be retrieved. If a list is provided, it should contain valid column names that exist in the database schema.

**Returns:**
`pandas.DataFrame`: A DataFrame containing the data retrieved from the SQLite database. The DataFrame will have columns corresponding to the specified fields in the query or all fields if no specific columns are requested.

**Detailed Logic:**
- The method begins by determining the SQL query to execute based on the provided `columns` parameter. If `columns` is `None`, it constructs a query to select all columns from the relevant database table.
- It then calls the `data_service.get_dataframe_from_sqlite` function, passing the database path and the constructed SQL query as arguments.
- The function retrieves the data from the SQLite database and returns it as a Pandas DataFrame.
- The method ensures that the data is loaded efficiently and is ready for further analysis or processing using Pandas' capabilities.

---
*Generated with 100% context confidence*
