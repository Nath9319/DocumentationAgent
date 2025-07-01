# Documentation for `FinancialService.calculate_payment`

### FinancialService.calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**
The `calculate_payment` method computes the fixed periodic payment required to fully amortize a loan over a specified number of payments. It utilizes the net present value formula to determine the payment amount based on the principal, annual interest rate, and total number of payments.

**Parameters:**
- `principal` (`float`): The total amount of the loan that needs to be repaid.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**
- `principal` should be a positive float, representing the loan amount.
- `annual_rate` should be a non-negative float; a value of 0.0 indicates no interest.
- `num_payments` should be a positive integer, representing the number of payment periods.

**Returns:**
`float`: The fixed payment amount to be made in each period, calculated to ensure the loan is fully paid off by the end of the payment term.

**Detailed Logic:**
- The method begins by checking if the annual interest rate is zero. In this case, it calculates the payment by dividing the principal evenly across all payment periods.
- If the annual interest rate is greater than zero, it calculates the periodic interest rate by dividing the annual rate by the number of payment periods per year (typically 12 for monthly payments).
- The method then applies the amortization formula using the `npf.pmt` function, which is likely sourced from an external financial library. This function computes the payment amount based on the principal, periodic interest rate, and total number of payments.
- The result is a fixed payment amount that ensures the loan is fully amortized by the end of the specified payment term.