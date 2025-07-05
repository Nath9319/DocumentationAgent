# Documentation for get_correlation_matrix

### get_correlation_matrix(db_path: str, table_name: str, columns: List[str]) -> Dict[str, Dict[str, float]]

**Description:**
The `get_correlation_matrix` function computes the Pearson correlation matrix for specified columns in a given database table. It first validates the input parameters to ensure that the specified columns exist and are numeric. Upon successful validation, it retrieves the relevant data from the database and calculates the correlation matrix, returning it in a structured dictionary format.

**Parameters:**
- `db_path` (`str`): The file path to the SQLite database from which data will be retrieved.
- `table_name` (`str`): The name of the table within the database that contains the data for correlation analysis.
- `columns` (`List[str]`): A list of column names for which the correlation matrix will be calculated.

**Expected Input:**
- `db_path` should be a valid string representing the path to an existing SQLite database file.
- `table_name` should be a valid string representing the name of a table within the database.
- `columns` should be a list of strings, each representing a column name. If this list is empty, the function will default to using all numeric columns in the specified table.

**Returns:**
`Dict[str, Dict[str, float]]`: A nested dictionary representing the Pearson correlation coefficients between the specified columns. The outer dictionary's keys are the column names, and the values are dictionaries where each key is another column name and the value is the correlation coefficient.

**Detailed Logic:**
- The function begins by validating the input parameters using the `validate_correlation_inputs` method from the `ValidationService`. This ensures that the specified columns exist in the table and are numeric.
- If validation fails, a `DataError` is raised, providing feedback on the nature of the validation issue.
- Upon successful validation, the function calls the `calculate_correlation_matrix` method from the `StatsService`, passing the database path, table name, and validated column names.
- The `calculate_correlation_matrix` method loads the relevant data from the database, computes the Pearson correlation matrix using the Pandas library, and returns the result as a dictionary.
- The final output is a structured representation of the correlation coefficients, which can be used for further analysis or reporting.

---
*Generated with 71% context confidence*
