# Documentation for `DualInput`

```python
class DualInput:
    """
    Model for operations requiring two numbers.

    This class serves as a foundation for mathematical operations that involve
    two numerical inputs. It encapsulates the two numbers and provides methods
    to retrieve and manipulate them as needed.

    Attributes:
        number1 (float): The first number for the operation.
        number2 (float): The second number for the operation.

    Methods:
        get_numbers(): Returns a tuple containing both numbers.
        set_numbers(num1, num2): Updates the two numbers with new values.
    """

    def __init__(self, number1: float, number2: float):
        """
        Initializes the DualInput instance with two numbers.

        Args:
            number1 (float): The first number for the operation.
            number2 (float): The second number for the operation.
        """
        self.number1 = number1
        self.number2 = number2

    def get_numbers(self) -> tuple:
        """
        Returns the two numbers as a tuple.

        Returns:
            tuple: A tuple containing number1 and number2.
        """
        return self.number1, self.number2

    def set_numbers(self, num1: float, num2: float):
        """
        Updates the two numbers with new values.

        Args:
            num1 (float): The new value for the first number.
            num2 (float): The new value for the second number.
        """
        self.number1 = num1
        self.number2 = num2
```

### Documentation Summary:
The `DualInput` class is designed to facilitate operations that require two numerical inputs. It includes methods for retrieving and updating these numbers, making it a versatile component for mathematical calculations in the application. The class is initialized with two numbers and provides a straightforward interface for interaction.