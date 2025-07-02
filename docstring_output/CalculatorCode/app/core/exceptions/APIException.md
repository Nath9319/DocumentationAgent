### APIException

**Description:**  
Custom base exception class for the API. This class is designed to facilitate the creation of a custom exception handler in the main application, allowing for structured JSON error messages to be returned when exceptions occur.

**Parameters / Attributes:**  
| Name     | Type   | Description                                         |
|----------|--------|-----------------------------------------------------|
| message  | str    | A descriptive message that explains the error.     |
| code     | int    | An optional error code that categorizes the error. |

**Expected Input:**  
• `message` should be a non-empty string.  
• `code` should be an integer, typically representing an HTTP status code or application-specific error code.

**Returns:**  
This class does not return a value but serves as a base class for other exceptions that may inherit from it.

**Detailed Logic:**  
• The `APIException` class is intended to be subclassed by other exception classes that represent specific error conditions in the API.  
• When an exception is raised, the custom exception handler in `main.py` can catch instances of `APIException` and format the error response as structured JSON.  
• The structured JSON typically includes the error message and code, making it easier for clients to understand the nature of the error.

**Raises / Errors:**  
• This class itself does not raise errors but can be used to raise specific exceptions that inherit from it.

**Usage Example:**  
```python
class NotFoundException(APIException):
    def __init__(self, message="Resource not found", code=404):
        super().__init__(message, code)

# Raising the custom exception
raise NotFoundException()
```