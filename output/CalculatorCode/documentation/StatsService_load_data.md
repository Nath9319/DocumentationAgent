# Documentation for `StatsService._load_data`

### StatsService._load_data(columns: Optional[List[str]] = None) -> pandas.DataFrame

**Description:**
The `_load_data` method is responsible for loading data from a SQLite database into a pandas DataFrame. It utilizes the `data_service.get_dataframe_from_sqlite` function to execute a SQL query and retrieve the data. If the `columns` parameter is not specified (i.e., it is `None`), the method will load all available columns from the database.

**Parameters:**
- `columns` (`Optional[List[str]]`): A list of column names to be loaded from the database. If set to `None`, all columns will be retrieved.

**Expected Input:**
- `columns` should be a list of strings representing the names of the columns to be fetched from the SQLite database. If no specific columns are desired, this parameter can be omitted or set to `None`.

**Returns:**
`pandas.DataFrame`: A DataFrame containing the data retrieved from the SQLite database. The DataFrame will include all columns if `columns` is `None`, or only the specified columns if a list is provided.

**Detailed Logic:**
- The method constructs a SQL query based on the provided `columns` parameter. If `columns` is `None`, it generates a query to select all columns from the relevant database table.
- It then calls the `data_service.get_dataframe_from_sqlite` function, passing the constructed SQL query and the path to the SQLite database.
- The results of the query execution are fetched and returned as a pandas DataFrame, allowing for further data manipulation and analysis.
- The method ensures that the data loading process is efficient and leverages the capabilities of the `data_service` to handle database interactions seamlessly.

---
*Generated with 100% context confidence*
