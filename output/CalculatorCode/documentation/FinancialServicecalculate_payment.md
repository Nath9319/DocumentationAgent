# Documentation for `FinancialService.calculate_payment`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### FinancialService.calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**
The `calculate_payment` method computes the fixed periodic payment required to fully amortize a loan over a specified number of payments. It utilizes the net present value formula to determine the payment amount based on the loan's principal, annual interest rate, and the total number of payments.

**Parameters:**
- `principal` (`float`): The total amount of the loan that is being borrowed.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**
- `principal` must be a positive float, representing the loan amount.
- `annual_rate` should be a non-negative float; a value of 0.0 indicates that there is no interest on the loan.
- `num_payments` must be a positive integer, indicating the number of payment periods (e.g., months or years).

**Returns:**
`float`: The fixed payment amount that must be paid in each period to fully amortize the loan.

**Detailed Logic:**
- The method first checks if the annual interest rate is zero. If it is, the payment is calculated by dividing the principal evenly across all payment periods.
- If the annual interest rate is greater than zero, the method calculates the periodic interest rate by dividing the annual rate by the number of payment periods per year (typically 12 for monthly payments).
- It then applies the amortization formula, which incorporates the principal, periodic interest rate, and total number of payments, to compute the periodic payment amount.
- The method relies on the `npf.pmt` function from an external library to perform the calculation, ensuring accurate results based on the financial principles of loan amortization.

---
*Generated with 0% context confidence*
