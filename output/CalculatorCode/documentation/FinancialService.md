# Documentation for `FinancialService`

### FinancialService

**Description:**
The `FinancialService` class provides a set of methods for performing common financial calculations, leveraging the capabilities of the `numpy_financial` library. It is designed to facilitate operations such as calculating future values, present values, and periodic payments associated with investments and loans.

**Parameters/Attributes:**
None (the class does not define any attributes in the provided lines).

**Expected Input:**
- The class methods expect inputs that conform to the types and constraints defined by the `numpy_financial` functions it utilizes. This includes:
  - `rate`: A non-negative float representing the interest rate per period.
  - `nper`: A positive integer indicating the total number of payment periods.
  - `pmt`: A float representing the payment amount per period, which can be negative for outflows.
  - `pv`: A float representing the present value, which can be zero or negative.
  - `when`: A string that specifies the timing of payments, either 'end' or 'begin'.

**Returns:**
The methods within the `FinancialService` class return various financial metrics, including:
- Future values (as `float`).
- Present values (as `float`).
- Periodic payment amounts (as `float`).

**Detailed Logic:**
- The `FinancialService` class encapsulates methods that call the `numpy_financial` functions: `npf.fv`, `npf.pv`, and `npf.pmt`.
- Each method within the class is responsible for validating input parameters to ensure they meet the expected types and constraints.
- The class methods utilize the respective financial formulas from the `numpy_financial` library to compute results:
  - For future value calculations, it applies the formula that incorporates the present value, periodic payments, and interest rate over the specified number of periods.
  - For present value calculations, it uses a formula that discounts future cash flows back to their present worth based on the interest rate and timing of payments.
  - For periodic payment calculations, it derives the fixed payment amount needed to amortize a loan or investment over the specified number of periods.
- The results are computed and returned as floats, providing essential financial insights for users. The class does not maintain state or attributes, focusing solely on computation through its methods.

---
*Generated with 100% context confidence*
