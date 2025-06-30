# Documentation for `CalculationError.__init__`

```python
def __init__(self, detail: str='A calculation error occurred.'):
    """
    Initializes a new instance of the CalculationError class.

    This constructor calls the parent class's initializer with a default 
    status code of 400 and a detail message that describes the error.

    Parameters:
        detail (str): A descriptive message about the calculation error. 
                      Defaults to 'A calculation error occurred.'.

    Raises:
        Exception: Propagates any exceptions raised by the parent class's 
                   initializer.
    """
    super().__init__(status_code=400, detail=detail)
``` 

### Documentation Overview

- **Method Name:** `__init__`
- **Class:** `CalculationError`
- **File Path:** `app/core/exceptions.py`
- **Lines:** 14 to 15

### Description
The `__init__` method is the constructor for the `CalculationError` class, which is used to create an instance of the error with a specific detail message. It inherits from a parent exception class and sets a default HTTP status code of 400, indicating a client-side error.

### Parameters
- **detail (str):** An optional string parameter that provides additional information about the error. If not specified, it defaults to "A calculation error occurred."

### Usage
This method is typically called when a calculation operation fails, allowing the application to raise a `CalculationError` with a relevant message for debugging or logging purposes.