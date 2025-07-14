# Documentation for `calculate_present_value`

### calculate_present_value(rate: float, num_periods: int, payment: float, future_value: float) -> float

**Description:**
This function serves as an API endpoint for calculating the present value of an investment based on the provided rate, number of periods, payment amount, and future value. It utilizes the financial service's `calculate_present_value` function to perform the core calculation, allowing users to determine how much a future cash flow is worth today.

**Parameters:**
- `rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_periods` (`int`): The total number of periods (years) until the future value is received.
- `payment` (`float`): The amount of money paid or received in each period.
- `future_value` (`float`): The amount of money expected to be received in the future.

**Expected Input:**
- `rate` should be a non-negative float, where 0.0 indicates no interest.
- `num_periods` should be a non-negative integer representing the time frame for the investment.
- `payment` should be a float representing the regular payment amount, which can be positive or negative depending on the cash flow direction.
- `future_value` should be a positive float representing the amount expected in the future.

**Returns:**
`float`: The present value of the future cash flow, indicating how much that future amount is worth today.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative values for rate and num_periods).
- It then calls the `financial_svc.calculate_present_value` function, passing the `future_value`, `rate`, and `num_periods` as arguments to compute the present value.
- The calculated present value is returned as a float, representing the current worth of the future cash flow.
- If any input values are invalid, the function raises a `ValueError` to indicate the issue, ensuring robust error handling and user feedback.

---
*Generated with 100% context confidence*
