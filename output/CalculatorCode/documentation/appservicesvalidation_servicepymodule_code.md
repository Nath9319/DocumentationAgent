# Documentation for `app\services\validation_service.py::module_code`

### ValidationService

**Description:**
The `ValidationService` class is designed to perform complex validations that span multiple services, ensuring that data requests are not only well-formed but also logically valid against the actual data in the database. It connects various models to the data layer, enabling thorough checks for data integrity and correctness.

**Parameters/Attributes:**
- `data_svc` (`DataService`): An instance of the `DataService` class that provides methods to interact with the database and retrieve data for validation purposes. This dependency is injected during the initialization of the `ValidationService`.

**Expected Input:**
- The `ValidationService` expects a `DataService` instance to be passed during initialization. This instance should be capable of querying the database and returning data in a format suitable for validation.
- The methods `validate_regression_inputs` and `validate_correlation_inputs` expect payloads of types `RegressionInput` and `CorrelationInput`, respectively. These payloads should contain the necessary attributes such as table names, column names, and paths to the database.

**Returns:**
- Both `validate_regression_inputs` and `validate_correlation_inputs` return `True` upon successful validation of the input data.
- If validation fails, these methods raise a `DataError` with a descriptive message indicating the nature of the failure.

**Detailed Logic:**
- The `ValidationService` class initializes with a `DataService` instance, which is used to fetch data from the database.
- The `validate_regression_inputs` method performs the following steps:
  1. It retrieves a DataFrame from the database using the provided database path and table name.
  2. It checks that all specified variables (dependent and independent) exist in the DataFrame's columns.
  3. It verifies that these columns are numeric and contain valid (non-null) data.
  4. If any checks fail, it raises a `DataError` with an appropriate message.
  
- The `validate_correlation_inputs` method follows a similar process:
  1. It retrieves the DataFrame from the database.
  2. It checks for the presence of specified columns, ensuring that at least two numeric columns are available for correlation analysis.
  3. It raises a `DataError` if any column is missing or not numeric.
  
- Both methods print success messages upon successful validation, indicating the completion of the validation process. The class effectively integrates model validation with data retrieval, ensuring robust data integrity checks across services.

---
*Generated with 100% context confidence*
