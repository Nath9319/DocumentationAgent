# Documentation for `CalculationError`

```markdown
# CalculationError Class Documentation

## Class: `CalculationError`
**File Path:** `app/core/exceptions.py`  
**Lines:** 13 to 15

### Description
The `CalculationError` class is a custom exception that is raised when a calculation operation fails. It inherits from the `APIException` class and is designed to provide a clear indication of client-side errors, specifically those related to calculations. The class sets a default HTTP status code of 400, which signifies a bad request.

### Constructor: `__init__`

#### Method Signature
```python
def __init__(self, detail: str='A calculation error occurred.'):
```

#### Parameters
- **detail (str):**  
  An optional string that provides a descriptive message about the calculation error. If not provided, it defaults to "A calculation error occurred."

#### Raises
- **Exception:**  
  Any exceptions raised by the parent class's initializer (`APIException`) will be propagated.

### Usage
The `__init__` method is invoked to create an instance of `CalculationError` when a calculation fails. This allows developers to raise the error with a specific message, which can be useful for debugging or logging purposes. For example:

```python
if not valid_calculation:
    raise CalculationError("Invalid input provided for calculation.")
```

This usage helps in identifying the nature of the error and facilitates better error handling in the application.
```