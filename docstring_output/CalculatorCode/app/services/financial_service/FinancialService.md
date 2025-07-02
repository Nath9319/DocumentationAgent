### FinancialService

**Description:**  
A service class for handling common financial calculations. It utilizes the `numpy_financial` library to perform various financial computations.

**Parameters / Attributes:**  
| Name          | Type               | Description                                      |
|---------------|--------------------|--------------------------------------------------|
| None          | None               | This class does not have any parameters or attributes defined in the docstring. |

**Expected Input:**  
• The class methods will accept various financial parameters such as principal, interest rates, and payment terms, which should conform to the expected data types defined in their respective method signatures.  
• Inputs should be validated to ensure they are within acceptable ranges (e.g., non-negative values for rates and terms).

**Returns:**  
The methods within this class will return various financial metrics, such as payment amounts, present values, or future values, depending on the specific calculation performed.

**Detailed Logic:**  
• The class serves as a wrapper around the `numpy_financial` library, which provides functions for financial calculations.  
• Each method within the class will call the appropriate function from the `numpy_financial` library, passing the necessary parameters to compute the desired financial metric.  
• The results from these computations will be returned to the caller, allowing for further processing or display.

**Raises / Errors:**  
• The class may raise exceptions related to invalid input types or values, such as `ValueError` for negative values where only positive values are acceptable.

**Usage Example:**  
```python
financial_service = FinancialService()
payment = financial_service.calculate_payment(principal=1000, annual_rate=0.05, num_payments=12)
print(payment)
```