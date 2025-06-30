# Documentation for `SingleInput`

```python
class SingleInput:
    """
    Model for operations requiring a single number.

    This class serves as a base for mathematical operations that
    take a single numerical input. It can be extended to implement
    specific operations such as square, square root, or any other
    unary operation.

    Attributes:
        value (float): The single numerical input for the operation.
    """

    def __init__(self, value: float):
        """
        Initializes the SingleInput instance with a given value.

        Args:
            value (float): The number to be used in the operation.
        """
        self.value = value
```

### Documentation Overview

#### Class: `SingleInput`

- **File Path:** `Calculator\app\models\calculator.py`
- **Lines:** 12 to 14

#### Description
The `SingleInput` class is designed to model mathematical operations that require only a single numerical input. It provides a foundation for creating various unary operations by encapsulating the input value.

#### Attributes
- **value (float)**: This attribute holds the single numerical input that will be used in the operation.

#### Initialization
- **`__init__(self, value: float)`**: Constructor method that initializes the `SingleInput` instance with a specified numerical value.

#### Usage
This class can be extended to implement specific operations that utilize the single input, such as:
- Squaring the input value
- Calculating the square root
- Any other unary mathematical operation

### Example
```python
# Example usage of SingleInput
single_input = SingleInput(4)
print(single_input.value)  # Output: 4
```

This documentation provides a clear understanding of the `SingleInput` class, its purpose, attributes, and potential usage within the codebase.