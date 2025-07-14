# Documentation for `calculate_future_value`

### calculate_future_value(rate: float, periods: int, payment: float, present_value: float) -> float

**Description:**
Calculates the future value of an investment based on the provided interest rate, number of periods, regular payment amount, and present value. This function is designed to facilitate financial forecasting by determining how much an investment will grow over time, taking into account both the initial investment and any additional payments made during the investment period.

**Parameters:**
- `rate` (`float`): The interest rate per period as a decimal (e.g., 0.05 for 5%).
- `periods` (`int`): The total number of periods (e.g., years, months) for which the investment is held.
- `payment` (`float`): The amount of money added to the investment at the end of each period.
- `present_value` (`float`): The initial amount of money that is being invested or saved.

**Expected Input:**
- `rate` should be a non-negative float, where 0.0 indicates no interest.
- `periods` should be a non-negative integer representing the total number of periods for the investment.
- `payment` should be a float representing the amount added to the investment at the end of each period.
- `present_value` should be a positive float representing the initial investment amount.

**Returns:**
`float`: The future value of the investment after the specified number of periods, including interest and additional payments.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure that `rate` is non-negative, `periods` is non-negative, `payment` is a valid float, and `present_value` is positive.
- It then calculates the future value using the formula for future value of an investment with regular payments:
  \[
  \text{Future Value} = \text{Present Value} \times (1 + \text{Rate})^{\text{Periods}} + \text{Payment} \times \left(\frac{(1 + \text{Rate})^{\text{Periods}} - 1}{\text{Rate}}\right)
  \]
- The first part of the formula accounts for the growth of the initial investment, while the second part calculates the accumulated value of the regular payments made over the investment period.
- Finally, the function returns the computed future value, representing the total amount accumulated after the investment period, including interest earned and additional payments made. 

This function is typically used in financial applications to help users understand the potential growth of their investments over time.

---
*Generated with 100% context confidence*
