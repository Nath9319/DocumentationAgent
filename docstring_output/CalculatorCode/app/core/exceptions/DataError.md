### DataError

**Description:**  
Represents an error related to data processing or manipulation within the application. This exception is typically raised when there is an issue with the integrity or validity of the data being handled.

**Parameters:**  
| Name      | Type   | Description                                      |
|-----------|--------|--------------------------------------------------|
| message   | str    | A descriptive message providing details about the error. |
| code      | int    | An optional error code that categorizes the error. |

**Expected Input:**  
• `message` should be a non-empty string that describes the error.  
• `code` should be a valid integer representing the error category, if provided.

**Returns:**  
This symbol does not return a value; it is used to raise an exception.

**Detailed Logic:**  
• When an instance of `DataError` is created, it initializes with a message and an optional error code.  
• The exception can be caught and handled by the application to provide feedback to the user or to log the error for debugging purposes.  
• It is typically used in scenarios where data validation fails or when data cannot be processed as expected.

**Raises / Errors:**  
• Raises a `DataError` when data integrity checks fail or when data processing encounters an unexpected condition.

**Usage Example:**  
```python
try:
    # Some data processing logic
    raise DataError("Invalid data format", code=1001)
except DataError as e:
    print(f"DataError occurred: {e.message} (Code: {e.code})")
```