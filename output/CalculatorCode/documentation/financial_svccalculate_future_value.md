# Documentation for `financial_svc.calculate_future_value`

### calculate_future_value(principal: float, annual_rate: float, years: int) -> float

**Description:**
Calculates the future value of an investment based on the principal amount, the annual interest rate, and the number of years the money is invested. This function uses the formula for compound interest to determine how much an investment will grow over time.

**Parameters:**
- `principal` (`float`): The initial amount of money that is being invested or saved.
- `annual_rate` (`float`): The annual interest rate as a decimal (e.g., 0.05 for 5%).
- `years` (`int`): The total number of years the money is invested or saved.

**Expected Input:**
- `principal` should be a positive float representing the initial investment amount.
- `annual_rate` should be a non-negative float, where 0.0 indicates no interest.
- `years` should be a non-negative integer, representing the duration of the investment.

**Returns:**
`float`: The future value of the investment after the specified number of years, including interest.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure that `principal` is positive, `annual_rate` is non-negative, and `years` is non-negative.
- It then calculates the future value using the compound interest formula: 
  \[
  \text{Future Value} = \text{Principal} \times (1 + \text{Annual Rate})^{\text{Years}}
  \]
- The result is computed by multiplying the principal by the growth factor, which is derived from the annual interest rate compounded over the specified number of years.
- Finally, the function returns the computed future value, which represents the total amount accumulated after the investment period, including interest earned.

---
*Generated with 100% context confidence*
