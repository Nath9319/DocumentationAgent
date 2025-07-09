# Documentation for `financial_svc.calculate_present_value`

### calculate_present_value(future_value: float, annual_rate: float, num_years: int) -> float

**Description:**
Calculates the present value of a future sum of money based on a specified annual interest rate and the number of years until the amount is received. This function is essential in finance for determining how much a future cash flow is worth today.

**Parameters:**
- `future_value` (`float`): The amount of money to be received in the future.
- `annual_rate` (`float`): The annual interest rate as a decimal (e.g., 0.05 for 5%).
- `num_years` (`int`): The number of years until the future value is received.

**Expected Input:**
- `future_value` should be a positive float representing the amount expected in the future.
- `annual_rate` should be a non-negative float (0.0 means no interest).
- `num_years` should be a non-negative integer, representing the time frame for the investment.

**Returns:**
`float`: The present value of the future cash flow, representing how much that future amount is worth today.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative values).
- It calculates the present value using the formula: 
  \[
  \text{Present Value} = \frac{\text{Future Value}}{(1 + \text{annual rate})^{\text{num years}}}
  \]
- This formula discounts the future value back to the present using the specified annual interest rate compounded over the number of years.
- The result is then returned as a float, representing the present value of the future cash flow.
- The function does not rely on any external dependencies and performs all calculations using basic arithmetic operations.

---
*Generated with 100% context confidence*
