# Documentation for `FinancialService`

```markdown
### FinancialService

**Description:**  
The `FinancialService` class provides a set of methods for performing common financial calculations, including future value, present value, and loan payment calculations. It leverages the `numpy_financial` library to facilitate these computations, ensuring accurate and efficient financial analysis.

**Parameters/Attributes:**  
None (the class does not have any attributes defined in the provided context).

**Expected Input:**  
- The methods within this class expect numerical inputs, specifically floats for monetary values and integers for time periods. Each method has its own constraints regarding the validity of these inputs, such as requiring non-negative values for rates and periods.

**Returns:**  
The methods of the `FinancialService` class return float values representing various financial metrics:
- Future value of an investment.
- Present value of future cash flows.
- Periodic payment amount for loans.

**Detailed Logic:**  
- The class contains multiple methods, each designed to handle specific financial calculations:
  - **calculate_future_value:** This method computes the future value of an investment using the compound interest formula. It validates the input parameters and applies the formula \( FV = P \times (1 + r)^n \) to determine the future worth of the principal amount.
  
  - **calculate_present_value:** This method calculates the present value of a future cash flow by applying the present value formula \( PV = \frac{FV}{(1 + r)^n} \). It ensures that the inputs are valid and performs the necessary arithmetic to derive the present value from the future amount.

  - **calculate_payment:** This method determines the fixed periodic payment required to amortize a loan over a specified number of payments. It checks if the annual interest rate is zero to handle cases without interest, and otherwise applies the loan amortization formula to compute the payment amount.

- Each method is designed to be self-contained, performing all necessary calculations using basic arithmetic operations and ensuring that inputs are validated before processing. The class does not maintain state or attributes, focusing solely on providing utility functions for financial calculations.
```