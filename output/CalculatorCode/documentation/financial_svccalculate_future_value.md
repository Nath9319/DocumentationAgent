# Documentation for `financial_svc.calculate_future_value`

### calculate_future_value(principal: float, annual_rate: float, years: int) -> float

**Description:**
Calculates the future value of an investment based on the initial principal, the annual interest rate, and the number of years the investment is held. This function uses the formula for compound interest to determine how much the investment will grow over time.

**Parameters:**
- `principal` (`float`): The initial amount of money invested or loaned.
- `annual_rate` (`float`): The annual interest rate as a decimal (e.g., 0.05 for 5%).
- `years` (`int`): The total number of years the money is invested or borrowed.

**Expected Input:**
- `principal` should be a positive float representing the initial investment amount.
- `annual_rate` should be a non-negative float (0.0 means no interest).
- `years` should be a non-negative integer, representing the duration of the investment.

**Returns:**
`float`: The future value of the investment after the specified number of years, including interest.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative values for `annual_rate` and `years`, and a positive value for `principal`).
- It then calculates the future value using the compound interest formula: 
  \[
  \text{Future Value} = \text{Principal} \times (1 + \text{Annual Rate})^{\text{Years}}
  \]
- The result is computed and returned as a float, representing the total amount accumulated after the specified period, including interest earned.
- This function does not rely on any external dependencies and performs calculations using basic arithmetic operations.

---
*Generated with 100% context confidence*
