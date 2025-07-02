# Documentation for `ValidationService.validate_regression_inputs`

> ⚠️ **Quality Notice**: Documentation generated with 41% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.

**Dependencies:**
- `print`
- `self.data_svc.get_dataframe_from_sqlite`
- `DataError`
- `pd.api.types.is_numeric_dtype`
- `df.columns`
- `df[var].isnull`
- `df[var]`
### ValidationService.validate_regression_inputs(payload: RegressionInput) -> None

**Description:**
The `validate_regression_inputs` method is responsible for validating the input data for regression analysis by ensuring that the specified columns exist in the database and that they contain numeric values. It connects the `RegressionInput` model with the `DataService` to perform comprehensive validation checks, ensuring data integrity before proceeding with regression analysis.

**Parameters:**
- `payload` (`RegressionInput`): A Pydantic model that encapsulates the request data for regression analysis, including the columns to be validated.

**Expected Input:**
- The `payload` parameter must be an instance of the `RegressionInput` model, which should contain the necessary attributes representing the columns intended for regression analysis. The attributes must be defined in accordance with the expected schema for regression inputs.

**Returns:**
`None`: This method does not return any value. Its primary function is to validate the input data and raise exceptions if any validation checks fail.

**Detailed Logic:**
- The method begins by retrieving the relevant data from the database using the `DataService` to obtain a DataFrame that corresponds to the columns specified in the `payload`.
- It then checks for the existence of each column listed in the `payload` within the DataFrame. If any column is missing, a `DataError` is raised to indicate the validation failure.
- Following the existence check, the method verifies that each specified column contains numeric data types. This is accomplished using the `pd.api.types.is_numeric_dtype` function, which checks the data type of each column.
- If any column fails the numeric check, the method raises a `DataError`, providing feedback on which specific column(s) did not meet the validation criteria.
- The method also checks for null values in the specified columns, raising a `DataError` if any null entries are found, thereby ensuring that the data is complete and valid for regression analysis.

---
*Generated with 41% context confidence*
