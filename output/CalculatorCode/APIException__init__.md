# Documentation for `APIException.__init__`

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

### Documentation Overview

- **Method Name:** `__init__`
- **Class:** `APIException`
- **File Path:** `app/core/exceptions.py`
- **Lines:** 7 to 10

### Description
The `__init__` method initializes an instance of the `APIException` class, which is used to represent exceptions that occur within an API context. It captures both an HTTP status code and a detailed message, allowing for better error handling and reporting.

### Parameters
- `status_code` (int): The HTTP status code that corresponds to the error being raised (e.g., 404 for "Not Found").
- `detail` (str): A descriptive message that provides additional context about the error.

### Behavior
Upon initialization, the method assigns the provided `status_code` and `detail` to the instance attributes. It also invokes the parent class's initializer with the `detail` message, ensuring that the exception can be raised with a meaningful message.

### Example Usage
To raise an `APIException` with a specific status code and message, you can use the following syntax:
```python
raise APIException(404, "Resource not found")
``` 

This example demonstrates how to create an exception that indicates a resource was not found, along with the appropriate HTTP status code.