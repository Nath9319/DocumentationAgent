# Documentation for `APIException`

# APIException Class Documentation

## Overview
The `APIException` class is a custom exception designed for use within an API context. It extends the built-in `Exception` class and provides a structured way to handle errors by associating them with HTTP status codes and detailed messages. This enables the implementation of a custom exception handler that can return structured JSON error responses.

### File Path
`app/core/exceptions.py`

### Class Definition
```python
class APIException(Exception):
    """
    Custom base exception class for the API.
    This allows us to create a custom exception handler in main.py
    to return structured JSON error messages.
    """
```

## Constructor: `__init__`

### Description
The `__init__` method initializes an instance of the `APIException` class. It captures an HTTP status code and a detailed message, which are essential for effective error reporting and handling in API responses.

### Parameters
- `status_code` (int): The HTTP status code associated with the error (e.g., `404` for "Not Found").
- `detail` (str): A detailed message that describes the nature of the error.

### Behavior
When an instance of `APIException` is created, the provided `status_code` and `detail` are stored as instance attributes. The method also calls the initializer of the parent `Exception` class with the `detail` message, ensuring that the exception can be raised with a meaningful description.

### Example Usage
To raise an `APIException`, you can use the following syntax:
```python
raise APIException(404, "Resource not found")
```
This example illustrates how to create an exception indicating that a resource was not found, along with the corresponding HTTP status code.

### Source Code
```python
def __init__(self, status_code: int, detail: str):
    """
    Initializes an instance of the APIException class.

    Parameters:
    ----------
    status_code : int
        The HTTP status code associated with the exception.
    detail : str
        A detailed message describing the exception.

    This constructor sets the status code and detail attributes for the 
    APIException instance and calls the parent class's initializer 
    with the detail message.

    Example:
    --------
    >>> raise APIException(404, "Resource not found")
    """
    self.status_code = status_code
    self.detail = detail
    super().__init__(self.detail)
```

This documentation provides a comprehensive overview of the `APIException` class and its constructor, facilitating better understanding and usage within the codebase.