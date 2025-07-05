# Documentation for FinancialService.calculate_payment

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### FinancialService.calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**
The `calculate_payment` method computes the fixed periodic payment required to fully amortize a loan over a specified number of payments. It utilizes the net present value formula to determine the payment amount based on the loan's principal, the annual interest rate, and the total number of payments.

**Parameters:**
- `principal` (`float`): The total amount of the loan that needs to be repaid.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**
- `principal` must be a positive float, representing the loan amount.
- `annual_rate` should be a non-negative float, where 0.0 indicates no interest.
- `num_payments` must be a positive integer, representing the number of payment periods.

**Returns:**
`float`: The fixed payment amount that must be paid in each period to fully amortize the loan.

**Detailed Logic:**
- The method first checks if the `annual_rate` is zero. If it is, the function calculates the payment by dividing the `principal` evenly across all `num_payments`.
- If the `annual_rate` is non-zero, it calculates the periodic interest rate by dividing the annual rate by 12 (to convert it to a monthly rate).
- The method then applies the standard amortization formula, which involves using the `npf.pmt` function from the external library to compute the payment amount based on the principal, periodic interest rate, and total number of payments.
- The result is the fixed payment amount that will be paid in each period, ensuring that the loan is fully paid off by the end of the specified payment term.

---
*Generated with 0% context confidence*
