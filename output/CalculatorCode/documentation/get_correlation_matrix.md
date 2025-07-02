# Documentation for `get_correlation_matrix`

### get_correlation_matrix(db_path: str, table_name: str, columns: List[str]) -> Dict[str, Dict[str, float]]

**Description:**
The `get_correlation_matrix` function computes the Pearson correlation matrix for specified columns within a given database table. It validates the input parameters to ensure that the required columns exist and are numeric before performing the correlation analysis. The resulting matrix is returned in a dictionary format, where each key represents a column, and the associated value is another dictionary containing the correlation coefficients with other columns.

**Parameters:**
- `db_path` (`str`): The file path to the SQLite database from which the data will be retrieved.
- `table_name` (`str`): The name of the table within the database that contains the data for correlation analysis.
- `columns` (`List[str]`): A list of column names for which the correlation matrix will be calculated. If not provided, the function will attempt to use all numeric columns in the specified table.

**Expected Input:**
- `db_path` should be a valid string representing the path to an existing SQLite database file.
- `table_name` should be a string that corresponds to a valid table name within the database.
- `columns` should be a list of strings representing the names of the columns to be analyzed. If this list is empty or not provided, the function will automatically select all numeric columns from the table.

**Returns:**
`Dict[str, Dict[str, float]]`: A dictionary representing the Pearson correlation matrix, where each key is a column name and its value is another dictionary mapping other column names to their respective correlation coefficients.

**Detailed Logic:**
- The function begins by validating the input parameters using the `validate_correlation_inputs` method from the `ValidationService`. This ensures that the specified columns exist in the database table and are of numeric type.
- If the validation is successful, the function retrieves the relevant data from the database using the `StatsService.calculate_correlation_matrix` method. This method loads the data and computes the Pearson correlation matrix.
- The resulting correlation matrix is formatted as a dictionary, which is then returned to the caller.
- If any validation errors occur (e.g., missing columns or non-numeric data), the function raises a `DataError`, which is a custom exception designed to handle such issues gracefully within the API context.

---
*Generated with 71% context confidence*
