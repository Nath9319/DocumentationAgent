# Documentation for `APIException`

```python
class APIException(Exception):
    """
    Custom base exception class for the API.

    This exception class is designed to facilitate the creation of structured
    JSON error messages in the API. It serves as a base class for all
    custom exceptions that may be raised within the API, allowing for
    consistent error handling and messaging.

    Attributes:
    ----------
    message : str
        A descriptive message that provides details about the exception.
    status_code : int
        An HTTP status code associated with the exception, indicating the
        type of error that occurred.

    Methods:
    -------
    __init__(self, message: str, status_code: int = 500):
        Initializes the APIException with a message and an optional status code.
    """

    def __init__(self, message: str, status_code: int = 500):
        """
        Initializes the APIException with a message and an optional status code.

        Parameters:
        ----------
        message : str
            A descriptive message that provides details about the exception.
        status_code : int, optional
            An HTTP status code associated with the exception (default is 500).
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
```

### Documentation Breakdown:

- **Class Name:** `APIException`
- **Category:** Class
- **File Path:** `Calculator\app\core\exceptions.py`
- **Lines:** 1 to 10

### Purpose:
The `APIException` class is a custom exception designed for use within the API. It allows for the creation of structured JSON error messages, enabling consistent error handling across the application.

### Attributes:
- **message (str):** 
  - Description: A descriptive message that provides details about the exception.
  
- **status_code (int):** 
  - Description: An HTTP status code associated with the exception, indicating the type of error that occurred. Defaults to 500 (Internal Server Error).

### Methods:
- **`__init__(self, message: str, status_code: int = 500):`**
  - Description: Initializes the `APIException` with a message and an optional status code.
  
  - **Parameters:**
    - **message (str):** A descriptive message that provides details about the exception.
    - **status_code (int, optional):** An HTTP status code associated with the exception (default is 500).

This documentation provides a comprehensive overview of the `APIException` class, detailing its purpose, attributes, and initialization method, ensuring that developers can effectively utilize it within the API's error handling framework.