# Documentation for `FutureValueInput`

```python
class FutureValueInput:
    """
    Model for Future Value calculation.

    This class is responsible for validating inputs related to future value calculations, ensuring that 
    cash flow conventions are adhered to. Specifically, it enforces the rule that cash outflows must be 
    represented as negative values, in line with standard financial practices.

    Attributes:
    ----------
    cash_flow : float
        The cash flow value to be validated, which should be zero or negative if it represents an outflow.

    Methods:
    -------
    cash_outflow_must_be_negative(cls, v: float, info):
        Validates that the cash flow value is negative, raising a ValueError if it is not.

    Raises:
    ------
    ValueError
        If the cash flow value is positive, indicating an invalid representation of cash outflow.
    """

    # Class implementation goes here
```

### Notes:
- The docstring has been expanded to include a brief overview of the class's purpose, attributes, and methods.
- The explanation of the cash flow validation has been clarified to emphasize the financial convention being enforced.
- The structure follows standard documentation practices, making it easy for users to understand the functionality and constraints of the `FutureValueInput` class.