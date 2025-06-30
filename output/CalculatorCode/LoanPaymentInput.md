# Documentation for `LoanPaymentInput`

```python
class LoanPaymentInput:
    """
    Model for Loan Payment calculation.

    This class serves as a data structure to hold the necessary inputs 
    for calculating loan payments. It encapsulates the parameters required 
    for the loan payment calculation process, ensuring that all relevant 
    data is organized and easily accessible.

    Attributes:
        principal (float): The total amount of the loan.
        annual_interest_rate (float): The annual interest rate as a percentage.
        loan_term_years (int): The duration of the loan in years.

    Methods:
        __init__(self, principal: float, annual_interest_rate: float, loan_term_years: int):
            Initializes a LoanPaymentInput instance with the specified loan parameters.
    """

    def __init__(self, principal: float, annual_interest_rate: float, loan_term_years: int):
        """
        Initializes a LoanPaymentInput instance with the specified loan parameters.

        Args:
            principal (float): The total amount of the loan.
            annual_interest_rate (float): The annual interest rate as a percentage.
            loan_term_years (int): The duration of the loan in years.
        """
        self.principal = principal
        self.annual_interest_rate = annual_interest_rate
        self.loan_term_years = loan_term_years
```

### Documentation Breakdown:

- **Class Overview**: The class is introduced as a model for loan payment calculations, providing context for its purpose.
- **Attributes**: Each attribute is clearly defined with its type and purpose, allowing users to understand what data they need to provide.
- **Constructor Method**: The `__init__` method is documented to explain how to instantiate the class, including parameter types and descriptions. 

This documentation provides a comprehensive understanding of the `LoanPaymentInput` class, making it easier for developers to utilize it effectively within the codebase.