### CalculationError

**Description:**  
Represents an error that occurs during a calculation process, indicating that the operation could not be completed successfully.

**Parameters:**  
| Name           | Type    | Description                                   |
|----------------|---------|-----------------------------------------------|
| message        | str     | A descriptive message explaining the error.  |
| code           | int     | An optional error code representing the type of calculation error. |

**Expected Input:**  
• `message` should be a non-empty string.  
• `code` should be an integer, typically representing specific error conditions.

**Returns:**  
This symbol does not return a value but raises an exception when invoked.

**Detailed Logic:**  
• The `CalculationError` is instantiated with a message and an optional error code.  
• It is designed to be raised in scenarios where a calculation cannot be completed due to invalid input, division by zero, or other mathematical inconsistencies.  
• The error can be caught and handled by the calling code to provide feedback to the user or to log the error for debugging purposes.

**Raises / Errors:**  
• Raises a `CalculationError` when a calculation fails due to invalid parameters or other issues.

**Usage Example:**  
```python
try:
    # Some calculation logic that may fail
    raise CalculationError("Invalid calculation attempt", code=1001)
except CalculationError as e:
    print(f"Error: {e.message} (Code: {e.code})")
```