# Documentation for `calculate_present_value`

### calculate_present_value(rate: float, num_periods: int, payment: float, future_value: float) -> float

**Description:**
Calculates the present value of an investment based on a specified interest rate, number of periods, payment amount, and future value. This function helps users understand how much an investment made today will be worth in the future, taking into account the time value of money.

**Parameters:**
- `rate` (`float`): The interest rate per period as a decimal (e.g., 0.05 for 5%).
- `num_periods` (`int`): The total number of periods (e.g., years or months) until the future value is realized.
- `payment` (`float`): The amount of money to be paid or received in each period.
- `future_value` (`float`): The amount of money expected to be received in the future.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `num_periods` should be a non-negative integer indicating the total number of periods.
- `payment` should be a float representing the cash flow per period, which can be positive or negative depending on whether it is an inflow or outflow.
- `future_value` should be a positive float representing the expected cash flow in the future.

**Returns:**
`float`: The present value of the investment, indicating how much needs to be invested today to achieve the specified future value, considering the periodic payments and interest rate.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative values for `rate` and `num_periods`).
- It calculates the present value using the formula that incorporates the future value, periodic payments, and the interest rate:
  \[
  \text{Present Value} = \frac{\text{Future Value}}{(1 + \text{rate})^{\text{num periods}}} + \text{Payment} \times \left(\frac{1 - (1 + \text{rate})^{-\text{num periods}}}{\text{rate}}\right)
  \]
- This formula discounts the future value back to the present and accounts for the series of payments made over the specified number of periods.
- The function does not interact with external modules and relies solely on basic arithmetic operations to perform the calculation.
- If any of the input values are invalid (e.g., negative where not allowed), the function raises a `ValueError` to signal the issue.

---
*Generated with 100% context confidence*
