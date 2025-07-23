# Documentation for StatsService._load_data

### StatsService._load_data() -> pd.DataFrame

**Description:**
The `_load_data` method is responsible for loading data from a specified SQLite database table into a pandas DataFrame. It utilizes the `DataService.get_dataframe_from_sqlite` method to perform the actual data retrieval. If no specific columns are requested, the method retrieves all columns from the specified table.

**Parameters:**
- `db_path` (`str`): The file path to the SQLite database from which data will be loaded.
- `table_name` (`str`): The name of the table within the SQLite database to load data from.
- `columns` (`Optional[List[str]]`): A list of column names to load. If set to `None`, all columns from the table will be retrieved.

**Expected Input:**
- `db_path` should be a valid string representing the path to an existing SQLite database file.
- `table_name` should be a valid string representing the name of an existing table within the database.
- `columns` can be either a list of strings specifying the desired columns or `None` to indicate that all columns should be loaded.

**Returns:**
`pd.DataFrame`: A pandas DataFrame containing the data retrieved from the specified table in the SQLite database.

**Detailed Logic:**
- The method begins by validating the provided database path and table name.
- It calls the `DataService.get_dataframe_from_sqlite` method, passing the `db_path` and `table_name` as arguments. This method connects to the SQLite database and executes a SQL query to retrieve the data.
- If the `columns` parameter is `None`, the SQL query selects all columns from the specified table.
- The retrieved data is then returned as a pandas DataFrame.
- If the database file does not exist or if the table is empty, appropriate exceptions are raised to inform the user of the issue.

---
*Generated with 99% context confidence*
