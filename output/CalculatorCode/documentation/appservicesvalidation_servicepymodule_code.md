# Documentation for `app\services\validation_service.py::module_code`

### ValidationService

**Description:**
The `ValidationService` class is designed to perform complex validations that extend beyond simple field checks in models. It connects various models to the data layer, ensuring that incoming requests are not only well-formed but also logically valid based on the actual data stored in the database. This service is particularly useful for validating inputs for regression and correlation analyses.

**Parameters/Attributes:**
- `data_svc` (`DataService`): An instance of the `DataService` class, which is used to interact with the data layer and retrieve data for validation purposes. This parameter is optional and defaults to a predefined `data_service`.

**Expected Input:**
- The `data_svc` parameter should be an instance of the `DataService` class, which provides methods for data retrieval. 
- The class methods `validate_regression_inputs` and `validate_correlation_inputs` expect payloads of type `RegressionInput` and `CorrelationInput`, respectively. These payloads should contain the necessary information for validation, such as database paths, table names, and variable names.

**Returns:**
- The methods `validate_regression_inputs` and `validate_correlation_inputs` return `True` if the validation is successful.
- If validation fails, they raise a `DataError` with a descriptive message indicating the nature of the failure.

**Detailed Logic:**
- Upon initialization, the `ValidationService` class establishes a dependency on the `DataService`, which is essential for fetching data from the database.
- The `validate_regression_inputs` method performs the following steps:
  1. It retrieves a DataFrame from the database using the specified database path and table name from the `RegressionInput` payload.
  2. It checks that all specified variables (dependent and independent) exist in the DataFrame's columns.
  3. It verifies that each variable is numeric and contains valid (non-null) data.
  4. If any checks fail, a `DataError` is raised with a specific message.
  
- The `validate_correlation_inputs` method follows a similar process:
  1. It retrieves the DataFrame from the database.
  2. It checks for the presence of the specified columns for correlation analysis, ensuring at least two numeric columns are available.
  3. It raises a `DataError` if any columns are missing or if they are not numeric.
  
- Both methods print success messages upon successful validation, providing feedback to the user about the validation process.

---
*Generated with 100% context confidence*
