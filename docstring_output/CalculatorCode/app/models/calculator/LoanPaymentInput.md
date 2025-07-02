### LoanPaymentInput

**Description:**  
Model for Loan Payment calculation, designed to encapsulate the necessary inputs for computing loan payments.

**Parameters / Attributes:**  
| Name           | Type   | Description                                      |
|----------------|--------|--------------------------------------------------|
| principal      | float  | The total amount of the loan.                    |
| annual_rate    | float  | The annual interest rate expressed as a decimal. |
| num_payments   | int    | The total number of payments to be made.         |

**Expected Input:**  
• `principal` must be a positive float.  
• `annual_rate` must be a non-negative float.  
• `num_payments` must be a positive integer.

**Returns:**  
`None` – This model does not return a value but is used to store input data for loan payment calculations.

**Detailed Logic:**  
• The model initializes with the provided parameters for principal, annual rate, and number of payments.  
• It serves as a structured way to hold the input values necessary for further calculations related to loan payments.  
• The attributes can be accessed and utilized by other components or functions that perform the actual loan payment calculations.

**Raises / Errors:**  
• ValueError if `principal` is less than or equal to zero.  
• ValueError if `annual_rate` is negative.  
• ValueError if `num_payments` is less than or equal to zero.

**Usage Example:**  
```python
loan_input = LoanPaymentInput(principal=100000, annual_rate=0.05, num_payments=360)
```