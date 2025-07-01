# Documentation for `FinancialService.calculate_future_value`

```markdown
### calculate_future_value(principal: float, annual_rate: float, years: int) -> float

**Description:**  
Calculates the future value of an investment based on the principal amount, the annual interest rate, and the number of years the investment is held. This function utilizes the formula for compound interest to determine how much an initial investment will grow over time.

**Parameters:**
- `principal` (`float`): The initial amount of money invested or loaned.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `years` (`int`): The total number of years the money is invested or borrowed.

**Expected Input:**  
- `principal` should be a positive float representing the initial investment amount.
- `annual_rate` should be a non-negative float; a value of 0.0 indicates no interest will be accrued.
- `years` should be a non-negative integer, representing the duration of the investment.

**Returns:**  
`float`: The future value of the investment after the specified number of years, taking into account the compound interest.

**Detailed Logic:**  
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative values for `annual_rate` and `years`).
- It then applies the compound interest formula: 
  \[
  FV = P \times (1 + r)^n
  \]
  where \( FV \) is the future value, \( P \) is the principal, \( r \) is the annual interest rate, and \( n \) is the number of years.
- The function computes the future value by multiplying the principal by the result of raising the sum of one plus the annual rate to the power of the number of years.
- Finally, the computed future value is returned as a float, representing the total amount accumulated after the investment period.
```