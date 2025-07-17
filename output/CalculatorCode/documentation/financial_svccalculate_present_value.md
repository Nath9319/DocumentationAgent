# Documentation for `financial_svc.calculate_present_value`

### calculate_present_value(future_value: float, annual_rate: float, num_years: int) -> float

**Description:**
Calculates the present value of a future cash flow, which represents the amount of money that needs to be invested today at a specified interest rate to equal a given future value after a certain number of years. This function utilizes the concept of time value of money, allowing users to understand how much future cash flows are worth in today's terms.

**Parameters:**
- `future_value` (`float`): The amount of money expected to be received in the future.
- `annual_rate` (`float`): The annual interest rate as a decimal (e.g., 0.05 for 5%).
- `num_years` (`int`): The number of years until the future value is received.

**Expected Input:**
- `future_value` should be a positive float representing the expected cash flow in the future.
- `annual_rate` should be a non-negative float (0.0 means no interest).
- `num_years` should be a non-negative integer, representing the time period until the future value is realized.

**Returns:**
`float`: The present value of the future cash flow, indicating how much needs to be invested today to achieve the future value.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative values for `annual_rate` and `num_years`).
- It calculates the present value using the formula: 
  \[
  \text{Present Value} = \frac{\text{Future Value}}{(1 + \text{annual rate})^{\text{num years}}}
  \]
- This formula discounts the future value back to the present by accounting for the interest that could have been earned over the specified number of years.
- The function does not interact with any external modules and relies solely on basic arithmetic operations to perform the calculation.

---
*Generated with 100% context confidence*
