# Documentation for `CalculationError`

```python
class CalculationError(Exception):
    """
    Exception raised for errors in the calculation process.

    This class extends the built-in Exception class to provide a specific
    error type for calculation-related issues. It can be used to signal
    problems encountered during mathematical computations or data processing
    within the application.

    Attributes:
    ----------
    message : str
        A description of the error encountered during the calculation.
    """

    def __init__(self, message: str):
        """
        Initializes the CalculationError with a specific error message.

        Parameters:
        ----------
        message : str
            A detailed message explaining the nature of the calculation error.
        """
        super().__init__(message)
```

### Documentation Breakdown:

- **Class Name:** `CalculationError`
- **Category:** Class
- **File Path:** `Calculator\app\core\exceptions.py`
- **Lines:** 13 to 15

### Purpose:
The `CalculationError` class is a custom exception designed to handle errors that occur during calculation processes within the application. By extending the built-in `Exception` class, it provides a specific error type that can be raised and caught in the context of mathematical operations.

### Attributes:
- **message (str):** 
  - Description: A string that contains a detailed explanation of the error that occurred during the calculation. This message is passed to the base `Exception` class upon initialization.

### Constructor:
- **`__init__(self, message: str)`**
  - Purpose: Initializes a new instance of `CalculationError` with a specified error message.
  - Parameters:
    - **message (str):** A string that describes the error encountered during the calculation process.

This documentation provides a comprehensive overview of the `CalculationError` class, detailing its purpose, attributes, and constructor, thereby assisting developers in understanding how to effectively use this exception in their code.