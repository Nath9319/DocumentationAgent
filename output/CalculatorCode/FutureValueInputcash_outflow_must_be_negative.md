# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

```python
def cash_outflow_must_be_negative(cls, v: float, info):
    """
    Validates that the cash outflow value is zero or negative.

    This method is a class-level validator for the fields 'pmt' and 'pv' in the 
    FutureValueInput model. It ensures that the values representing cash outflows 
    are not positive, as a positive value would be inconsistent with the 
    definition of cash outflow.

    Args:
        cls: The class that this method is bound to.
        v (float): The value to validate, representing a cash outflow.
        info: Metadata about the field being validated, including the field name.

    Raises:
        ValueError: If the provided value `v` is greater than zero, indicating 
                     that cash outflow must be zero or negative.

    Returns:
        float: The validated cash outflow value, which is guaranteed to be 
               zero or negative.
    """
```