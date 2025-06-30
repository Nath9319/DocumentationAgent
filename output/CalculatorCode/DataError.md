# Documentation for `DataError`

```python
class DataError(Exception):
    """
    Exception raised for errors in data processing.

    This class extends the built-in Exception class to provide a specific 
    error type for data-related issues within the application. It can be 
    used to signal problems such as invalid data formats, missing data, 
    or any other data integrity issues that may arise during processing.

    Attributes:
    ----------
    message : str
        A description of the error encountered.
    """

    def __init__(self, message: str):
        """
        Initializes the DataError with a specific error message.

        Parameters:
        ----------
        message : str
            A description of the data error that occurred.
        """
        super().__init__(message)
        self.message = message
```

### Documentation Breakdown for `DataError` Class:

- **Class Name:** `DataError`
- **Category:** Class
- **File Path:** `Calculator\app\core\exceptions.py`
- **Lines:** 17 to 19

### Purpose:
The `DataError` class is a custom exception designed to handle errors specifically related to data processing within the application. It provides a clear mechanism for signaling issues that may arise due to invalid or corrupt data.

### Attributes:
- **message (str):** 
  - Description: A string that contains a description of the error encountered during data processing.

### Constructor:
- **`__init__(self, message: str)`**
  - Purpose: Initializes a new instance of the `DataError` class with a specified error message.
  - Parameters:
    - **message (str):** A detailed description of the data error that occurred, which will be passed to the base `Exception` class.

This documentation provides a comprehensive overview of the `DataError` class, detailing its purpose, attributes, and constructor, thereby enabling developers to effectively utilize this exception in their error handling strategies within the codebase.
