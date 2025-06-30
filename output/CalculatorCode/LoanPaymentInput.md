# Documentation for `LoanPaymentInput`

```python
class LoanPaymentInput(BaseModel):
    """
    Model for Loan Payment calculation.

    This class represents the input parameters required to calculate loan payments.
    It inherits from BaseModel and utilizes Pydantic's Field for data validation.

    Attributes:
        rate (float): The interest rate per period. Must be greater than 0.
        nper (int): The total number of payment periods. Must be greater than 0.
        pv (float): The present value or principal of the loan. Must be a positive value.

    Example:
        loan_input = LoanPaymentInput(rate=5.0, nper=60, pv=30000)
    """

    rate: float = Field(..., gt=0, description='Interest rate per period')
    nper: int = Field(..., gt=0, description='Total number of payment periods')
    pv: float = Field(..., gt=0, description='Present value or principal of the loan (must be positive)')
``` 

### Documentation Breakdown:

- **Class Purpose**: The `LoanPaymentInput` class is designed to encapsulate the necessary parameters for calculating loan payments, ensuring that the inputs are valid through the use of Pydantic's validation features.
  
- **Attributes**:
  - `rate`: Represents the interest rate applied to the loan. It must be a positive float.
  - `nper`: Indicates the total number of payment periods for the loan. It must be a positive integer.
  - `pv`: The present value or principal amount of the loan, which must also be a positive float.

- **Example Usage**: An example is provided to demonstrate how to instantiate the class with valid parameters.