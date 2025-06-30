# Documentation for `FutureValueInput`

```python
class FutureValueInput(BaseModel):
    """
    Model for Future Value calculation. Validates cash flow conventions.

    This class represents the input parameters required for calculating the future value of an investment 
    or cash flow. It ensures that the cash flow conventions are adhered to, specifically that cash outflows 
    are represented as negative values.

    Attributes:
        rate (float): Interest rate per period (e.g., 0.05 for 5%). Must be greater than 0.
        nper (int): Total number of payment periods. Must be greater than 0.
        pmt (float): Payment made each period. Conventionally negative for cash outflow.
        pv (float): Present value. Conventionally negative for cash outflow.

    Validators:
        - cash_outflow_must_be_negative: Ensures that the 'pmt' and 'pv' values are zero or negative, 
          as they represent cash outflows.
    """
    rate: float = Field(..., gt=0, description='Interest rate per period (e.g., 0.05 for 5%)')
    nper: int = Field(..., gt=0, description='Total number of payment periods')
    pmt: float = Field(..., description='Payment made each period (conventionally negative for cash outflow)')
    pv: float = Field(..., description='Present value (conventionally negative for cash outflow)')

    @field_validator('pmt', 'pv')
    @classmethod
    def cash_outflow_must_be_negative(cls, v: float, info):
        if v > 0:
            raise ValueError(f"'{info.field_name}' represents cash outflow and should be zero or negative.")
        return v
``` 

### Key Points:
- The `FutureValueInput` class is designed to encapsulate the parameters necessary for future value calculations.
- It includes validation to ensure that cash outflows are represented correctly, preventing positive values for `pmt` and `pv`.
- Each attribute is documented with its purpose and constraints, enhancing clarity for users of the class.