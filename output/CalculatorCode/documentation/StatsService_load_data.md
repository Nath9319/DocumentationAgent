# Documentation for `StatsService._load_data`

```markdown
### StatsService._load_data(columns: Optional[List[str]] = None) -> pd.DataFrame

**Description:**  
Loads data from an SQLite database into a pandas DataFrame. The method retrieves data based on the specified columns. If no columns are specified (i.e., `columns` is `None`), it loads all available columns from the database.

**Parameters:**
- `columns` (`Optional[List[str]]`): A list of column names to be loaded from the database. If set to `None`, all columns will be loaded.

**Expected Input:**  
- `columns` should be a list of strings representing the names of the columns to retrieve. If no specific columns are desired, this parameter can be omitted or set to `None`.

**Returns:**  
`pd.DataFrame`: A pandas DataFrame containing the data retrieved from the SQLite database. The structure of the DataFrame will depend on the specified columns or the entire dataset if no columns are provided.

**Detailed Logic:**  
- The method begins by establishing a connection to the SQLite database.
- It constructs a SQL query to select data. If `columns` is provided, the query will specify those columns; otherwise, it will use a wildcard to select all columns.
- The query is executed against the database, and the results are fetched.
- The fetched data is then converted into a pandas DataFrame, which is returned to the caller.
- This method does not have any internal dependencies and operates solely on the database connection and pandas library for data manipulation.
```