# Documentation for `financial_svc.calculate_payment`

### calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**
The `calculate_payment` function computes the fixed periodic payment required to fully amortize a loan over a specified number of payments. It utilizes the net present value formula to determine the payment amount, ensuring that the loan is paid off completely by the end of the payment term.

**Parameters:**
- `principal` (`float`): The total amount of the loan that is being borrowed.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**
- `principal` must be a positive float, representing the loan amount.
- `annual_rate` should be a non-negative float, where 0.0 indicates no interest charged.
- `num_payments` must be a positive integer, indicating the number of payment periods.

**Returns:**
`float`: The fixed payment amount that must be paid in each period to fully amortize the loan.

**Detailed Logic:**
- The function begins by checking if the `annual_rate` is zero. In this case, it calculates the payment by dividing the `principal` evenly across all `num_payments`.
- If the `annual_rate` is greater than zero, it computes the monthly interest rate by dividing the `annual_rate` by 12.
- The function then applies the standard amortization formula, which accounts for both the principal and the interest, to derive the fixed periodic payment amount.
- Throughout its execution, the function relies solely on basic arithmetic operations and does not call any external modules or functions.

---
*Generated with 100% context confidence*
