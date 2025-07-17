# Documentation for `ValidationService.validate_correlation_inputs`

### ValidationService.validate_correlation_inputs(payload: CorrelationInput)

**Description:**
The `validate_correlation_inputs` method is responsible for validating the inputs required for performing a correlation analysis. It ensures that the specified columns exist within the dataset and that these columns contain numeric data types. This validation is crucial for preventing runtime errors during the correlation computation.

**Parameters:**
- `payload` (`CorrelationInput`): An instance of the Pydantic model that encapsulates the input data for correlation analysis. This model includes the necessary attributes that specify the columns to be validated.

**Expected Input:**
- The `payload` parameter must be an instance of the `CorrelationInput` model, which should contain attributes that reference the columns intended for correlation analysis. The columns specified in the payload must exist in the underlying dataset and must be of a numeric data type.

**Returns:**
`None`: The method does not return a value. Instead, it performs validation checks and raises exceptions if the validation fails.

**Detailed Logic:**
- The method begins by extracting the column names from the `payload` that are intended for correlation analysis.
- It then retrieves the dataset, typically from a SQLite database, using a service method (`self.data_svc.get_dataframe_from_sqlite`).
- The method checks if each specified column exists in the dataset. If any column is missing, it raises a `DataError` with an appropriate message.
- Subsequently, it verifies that each of the specified columns is of a numeric data type using the `pd.api.types.is_numeric_dtype` function from the Pandas library. If any column fails this check, it raises a `DataError` indicating the issue.
- Throughout the process, the method may utilize the `print` function to output relevant debugging information to the console, aiding in the identification of validation issues during development or troubleshooting.

---
*Generated with 72% context confidence*
