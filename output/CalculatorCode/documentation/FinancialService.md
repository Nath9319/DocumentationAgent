# Documentation for `FinancialService`

### FinancialService

**Description:**
The `FinancialService` class is designed to facilitate common financial calculations, leveraging the capabilities of the `numpy_financial` library. It provides methods to compute future values, present values, and periodic payments, which are essential for various financial analyses and decision-making processes.

**Parameters/Attributes:**
None.

**Expected Input:**
The methods within the `FinancialService` class expect numerical inputs such as floats or integers representing financial values (e.g., principal amounts, interest rates, number of periods). The specific requirements for each method will depend on the financial calculation being performed.

**Returns:**
The methods of the `FinancialService` class return numerical values (floats) that represent the results of the financial calculations, such as future value, present value, or payment amount.

**Detailed Logic:**
- The class utilizes the `numpy_financial` library, which provides functions for financial calculations:
  - `npf.fv`: Computes the future value of an investment based on periodic, constant payments and a constant interest rate.
  - `npf.pv`: Calculates the present value of a cash flow or series of cash flows, given a specific interest rate.
  - `npf.pmt`: Determines the fixed periodic payment required to fully amortize a loan over a specified number of payments.
- Each method within the class encapsulates the logic for these calculations, allowing users to easily perform complex financial computations without needing to understand the underlying formulas.
- The class is structured to ensure that inputs are validated and appropriate exceptions are raised for invalid data, enhancing robustness and usability.