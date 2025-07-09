# Documentation for `financial_svc.calculate_payment`

### calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**
The `calculate_payment` function computes the fixed periodic payment required to fully amortize a loan over a specified number of payments. It utilizes the net present value formula to determine the payment amount based on the loan's principal, the annual interest rate, and the total number of payments.

**Parameters:**
- `principal` (`float`): The total amount of the loan that needs to be repaid.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**
- `principal` must be a positive float, representing the loan amount.
- `annual_rate` should be a non-negative float, where a value of 0.0 indicates that there is no interest charged on the loan.
- `num_payments` must be a positive integer, indicating the number of payment periods (e.g., months or years).

**Returns:**
`float`: The fixed payment amount that must be paid in each period to fully amortize the loan by the end of the specified number of payments.

**Detailed Logic:**
- The function begins by checking if the `annual_rate` is zero. If it is, the function calculates the payment by dividing the `principal` evenly across all `num_payments`.
- If the `annual_rate` is greater than zero, the function calculates the periodic interest rate by dividing the `annual_rate` by 12 (assuming monthly payments).
- It then applies the standard amortization formula, which incorporates the principal, the periodic interest rate, and the number of payments to compute the fixed payment amount.
- The function performs all calculations using basic arithmetic operations and does not rely on any external modules or libraries.

---
*Generated with 100% context confidence*
