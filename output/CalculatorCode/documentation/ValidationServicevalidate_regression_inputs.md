# Documentation for `ValidationService.validate_regression_inputs`

### ValidationService.validate_regression_inputs(payload: RegressionInput) -> None

**Description:**
The `validate_regression_inputs` method is responsible for validating the input data required for regression analysis. It connects to the database to ensure that the specified columns exist and are of a numeric type. This method serves as a critical validation step before proceeding with regression computations, ensuring data integrity and correctness.

**Parameters:**
- `payload` (`RegressionInput`): A Pydantic model that encapsulates the request data for regression analysis. This model includes the necessary attributes that define the regression input.

**Expected Input:**
- The `payload` must be an instance of the `RegressionInput` model, which should contain attributes corresponding to the columns expected in the regression analysis. The attributes must adhere to the expected data types and formats, specifically requiring that the columns referenced in the payload exist in the database and are numeric.

**Returns:**
`None`: This method does not return a value. Instead, it raises exceptions if validation checks fail.

**Detailed Logic:**
- The method begins by retrieving a DataFrame from the database using the `self.data_svc.get_dataframe_from_sqlite` function, which queries the relevant data based on the input provided in the `payload`.
- It then checks the existence of each specified column in the DataFrame. If any column is missing, a `DataError` is raised, indicating the specific column that is absent.
- For each column that exists, the method verifies whether the data type is numeric by utilizing `pd.api.types.is_numeric_dtype`. If a column is found to be non-numeric, a `DataError` is raised, specifying the column that failed the numeric check.
- Additionally, the method checks for null values in each column using `df[var].isnull()`. If any null values are detected, a `DataError` is raised, indicating that the column contains invalid data.
- Overall, the method ensures that all necessary validations are performed, providing a robust mechanism for data integrity before regression analysis is conducted.