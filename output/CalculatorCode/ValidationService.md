# Documentation for `ValidationService`

# ValidationService Documentation

## Overview
The `ValidationService` class is designed to perform complex, cross-service validations that extend beyond simple model field checks. It connects various models to the data layer, ensuring that requests are not only well-formed but also logically valid against the actual data stored in the database.

## File Path
`Calculator/app/services/validation_service.py`

## Class Definition
```python
class ValidationService:
    def __init__(self, data_svc: DataService = data_service):
        ...
```

### Constructor: `__init__`

#### Purpose
The `__init__` function serves as the constructor for the `ValidationService` class, establishing a dependency on the `DataService`. This allows the `ValidationService` to utilize the functionalities provided by the `DataService` for its operations.

#### Parameters
- **data_svc** (`DataService`, optional): 
  - An instance of `DataService` that the `ValidationService` will use. 
  - **Default**: If not specified, a default instance named `data_service` will be utilized.

#### Attributes
- **data_svc** (`DataService`): 
  - The `DataService` instance that is assigned to the `ValidationService`, enabling it to perform validation tasks.

### Method: `validate_regression_inputs`

#### Purpose
The `validate_regression_inputs` method validates the inputs required for regression analysis. It connects to the database to ensure that the specified columns exist in the given table and that they contain numeric data suitable for regression modeling.

#### Parameters
- **payload** (`RegressionInput`): A Pydantic model containing the request data, which includes:
  - `db_path`: The path to the database.
  - `table_name`: The name of the table to validate.
  - `dependent_var`: The dependent variable for the regression analysis.
  - `independent_vars`: A list of independent variables for the regression analysis.

#### Raises
- **DataError**: Raised if any of the following validation checks fail:
  - The specified column does not exist in the table.
  - The column data type is not numeric.
  - The column contains only null values.

#### Returns
- **bool**: Returns `True` upon successful validation.

#### Example Usage
```python
payload = RegressionInput(
    db_path="path/to/database.db",
    table_name="my_table",
    dependent_var="target_variable",
    independent_vars=["feature1", "feature2"]
)

try:
    validation_service.validate_regression_inputs(payload)
except DataError as e:
    print(f"Validation failed: {e}")
```

### Method: `validate_correlation_inputs`

#### Purpose
The `validate_correlation_inputs` method validates that the specified columns for a correlation analysis exist in the given table and are of numeric type. It ensures that the columns provided in the `payload` exist in the DataFrame retrieved from the specified SQLite database.

#### Parameters
- **payload** (`CorrelationInput`): The Pydantic model containing the correlation analysis parameters, including the database path, table name, and columns to validate.

#### Raises
- **DataError**: Raised if validation fails due to:
  - Fewer than two numeric columns specified.
  - Any specified column does not exist in the DataFrame.
  - Any specified column is not of numeric type.

#### Returns
- **bool**: Returns `True` if validation is successful.

#### Example Usage
```python
payload = CorrelationInput(
    db_path="path/to/database.db",
    table_name="my_table",
    columns=["feature1", "feature2"]
)

try:
    validation_service.validate_correlation_inputs(payload)
except DataError as e:
    print(f"Validation failed: {e}")
```

## Notes
- The `ValidationService` class integrates data models with a data service to perform comprehensive validation checks.
- Ensure that the `DataService` is properly initialized and accessible within the context where these methods are called.