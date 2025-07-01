# Documentation for `FinancialService.calculate_payment`

```markdown
### calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**  
Calculates the periodic payment required to fully amortize a loan over a specified number of payments, utilizing the principles of financial mathematics.

**Parameters:**
- `principal` (`float`): The total amount of the loan that is being borrowed.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**  
- `principal` must be a positive float, representing the amount of money borrowed.
- `annual_rate` should be a non-negative float, where 0.0 indicates no interest charged on the loan.
- `num_payments` must be a positive integer, indicating how many payments will be made.

**Returns:**  
`float`: The amount of each periodic payment that must be made to fully repay the loan by the end of the payment term.

**Detailed Logic:**  
- The method begins by checking if the `annual_rate` is zero. If it is, the function calculates the payment by simply dividing the `principal` by `num_payments`, as there is no interest to account for.
- If the `annual_rate` is greater than zero, the function computes the monthly interest rate by dividing the `annual_rate` by 12.
- It then applies the standard loan amortization formula to determine the fixed periodic payment amount. This formula takes into account the principal, the interest rate, and the number of payments to calculate how much needs to be paid each period to ensure the loan is fully repaid by the end of the term.
- The method does not rely on any external libraries or modules, performing all calculations using basic arithmetic operations.
```