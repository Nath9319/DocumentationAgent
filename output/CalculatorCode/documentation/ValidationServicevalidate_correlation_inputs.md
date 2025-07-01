# Documentation for `ValidationService.validate_correlation_inputs`

### validate_correlation_inputs(payload: CorrelationInput)

**Description:**
The `validate_correlation_inputs` method is responsible for validating the inputs required for performing a correlation analysis. It ensures that the specified columns in the provided payload exist within the data source and that these columns contain numeric data types. This validation is crucial for preventing errors during the correlation computation process.

**Parameters:**
- `payload` (`CorrelationInput`): An instance of the Pydantic model that encapsulates the input data for correlation analysis. This model includes the necessary fields that specify which columns to validate.

**Expected Input:**
- The `payload` should be an instance of `CorrelationInput`, which must define the columns intended for correlation analysis. The columns specified in this model should exist in the underlying data source and must be of a numeric data type (e.g., integers or floats). If any specified column is missing or non-numeric, validation will fail.

**Returns:**
`None`: The method does not return a value. Instead, it raises an exception if validation fails.

**Detailed Logic:**
- The method begins by retrieving the relevant data from a SQLite database using the `self.data_svc.get_dataframe_from_sqlite` method. This function call fetches the data necessary for validation.
- It then iterates through the columns specified in the `payload`. For each column, it checks if the column exists in the retrieved DataFrame.
- If a column is found to be missing, the method raises a `DataError`, providing a message that indicates which column is absent.
- For columns that exist, the method further checks whether the data type of each column is numeric by utilizing the `pd.api.types.is_numeric_dtype` function from the pandas library.
- If any column is found to be non-numeric, the method raises a `DataError` with a message indicating the specific column that failed the numeric check.
- The overall flow ensures that only valid and appropriate data is processed for correlation analysis, thereby enhancing the robustness of the application.