# Documentation for `get_correlation_matrix`

### get_correlation_matrix(db_path: str, table_name: str, columns: List[str]) -> Dict[str, Dict[str, float]]

**Description:**
The `get_correlation_matrix` function computes the Pearson correlation matrix for specified numeric columns within a given database table. It first validates the input parameters to ensure that the specified columns exist and are numeric, and then it calculates the correlation matrix using the validated data.

**Parameters:**
- `db_path` (`str`): The file path to the SQLite database from which data will be retrieved.
- `table_name` (`str`): The name of the table in the database that contains the data for correlation analysis.
- `columns` (`List[str]`): A list of column names for which the correlation matrix will be calculated.

**Expected Input:**
- `db_path` should be a valid string representing the path to an existing SQLite database file.
- `table_name` should be a valid string representing the name of a table within the database.
- `columns` should be a list of strings, each representing the name of a column in the specified table. At least two numeric columns must be provided for correlation analysis.

**Returns:**
`Dict[str, Dict[str, float]]`: A dictionary representing the Pearson correlation matrix, where the keys are the column names and the values are dictionaries mapping each column to its correlation coefficients with other specified columns.

**Detailed Logic:**
- The function begins by validating the input parameters using the `validate_correlation_inputs` method from the `ValidationService`. This ensures that the specified columns exist in the table and are of numeric type.
- If the validation is successful, the function then calls the `calculate_correlation_matrix` method from the `StatsService`. This method retrieves the relevant data from the database and computes the Pearson correlation matrix.
- The resulting correlation matrix is formatted as a dictionary, where each key corresponds to a column name and the associated value is another dictionary containing correlation coefficients with other columns.
- If any validation errors occur during the input validation phase, an `APIException` is raised, providing a structured error response to the client.

---
*Generated with 71% context confidence*
