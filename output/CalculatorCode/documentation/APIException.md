# Documentation for `APIException`


### APIException

**Description:**  
The `APIException` class serves as a custom base exception specifically designed for handling errors within the API. It facilitates the creation of structured JSON error messages, enabling a consistent response format for clients when exceptions occur. This class is intended to be used in conjunction with a custom exception handler defined in the main application logic.

**Parameters/Attributes:**
- `message` (`str`): A descriptive message that provides details about the exception.
- `status_code` (`int`): An integer representing the HTTP status code associated with the exception.

**Expected Input:**  
- `message` should be a string that conveys the nature of the error, providing context for the exception raised.
- `status_code` should be an integer corresponding to a valid HTTP status code (e.g., 404 for Not Found, 500 for Internal Server Error).

**Returns:**  
`None`: This class does not return a value; it initializes an instance of the `APIException`.

**Detailed Logic:**  
- The constructor of the `APIException` class first invokes the parent class's constructor to ensure that any necessary initialization from the base class is performed.
- It then assigns the provided `message` and `status_code` to the instance attributes, which can be accessed later when the exception is raised or logged.
- The primary function of this class is to encapsulate error information, allowing for structured error handling throughout the application without implementing complex logic or calculations.
