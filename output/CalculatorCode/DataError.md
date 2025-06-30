# Documentation for `DataError`

# Documentation for `DataError`

## Class: `DataError`

**Category:** Class  
**File Path:** `app/core/exceptions.py`  
**Lines:** 17 to 19  

### Description
The `DataError` class is a custom exception that inherits from `APIException`. It is designed to represent errors that occur during data processing, such as validation failures or unexpected data formats. This exception provides a mechanism to communicate specific error details to the caller while maintaining a standard HTTP status code.

### Inheritance
- Inherits from: `APIException`

### Constructor: `__init__`

#### Method: `__init__`

**Category:** Method  
**File Path:** `app/core/exceptions.py`  
**Lines:** 18 to 19  

#### Description
The `__init__` method initializes a new instance of the `DataError` class. It sets a default error message and a status code for the exception, which is fixed at `400`, indicating a client-side error.

#### Parameters
- **detail** (`str`, optional): A descriptive message that provides details about the error. Defaults to `'An error occurred while processing data.'`.

#### Example Usage
```python
try:
    # Some data processing logic
    raise DataError("Invalid data format.")
except DataError as e:
    print(e.detail)  # Output: Invalid data format.
```

#### Notes
- The `DataError` class is typically used in scenarios where data validation or processing fails, allowing for clear communication of the error to the caller.
- The default message can be overridden by providing a custom message when raising the exception.

### Summary
The `DataError` class serves as a specialized exception for handling data-related issues, enhancing error reporting and debugging in applications that require robust data processing capabilities.