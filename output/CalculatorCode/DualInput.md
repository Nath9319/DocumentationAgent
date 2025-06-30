# Documentation for `DualInput`

```python
class DualInput(BaseModel):
    """Model for operations requiring two numbers.

    This class serves as a data model for operations that involve two numerical inputs.
    It inherits from the BaseModel and defines two attributes, `number1` and `number2`, 
    both of which are expected to be of type float.

    Attributes:
        number1 (float): The first number for the operation.
        number2 (float): The second number for the operation.
    """
    number1: float
    number2: float
``` 

### Documentation Breakdown:

- **Class Name:** `DualInput`
- **Category:** Class
- **File Path:** `app/models/calculator.py`
- **Purpose:** To model operations that require two numerical inputs.
- **Attributes:**
  - `number1`: A float representing the first number.
  - `number2`: A float representing the second number.

This documentation provides a clear understanding of the class's purpose and its attributes, making it easier for developers to utilize the `DualInput` class effectively within the codebase.