# Documentation for `calculate_future_value`

### calculate_future_value(rate: float, periods: int, payment: float, present_value: float) -> float

**Description:**
Calculates the future value of an investment based on the specified interest rate, number of periods, periodic payment, and present value. This function is designed to provide users with an estimate of how much their investment will grow over time, taking into account regular contributions and the effect of compounding interest.

**Parameters:**
- `rate` (`float`): The interest rate per period as a decimal (e.g., 0.05 for 5%).
- `periods` (`int`): The total number of periods (e.g., years, months) over which the investment is made.
- `payment` (`float`): The amount of money added to the investment at the end of each period.
- `present_value` (`float`): The initial amount of money invested or the present value of the investment.

**Expected Input:**
- `rate` should be a non-negative float, where 0.0 indicates no interest.
- `periods` should be a non-negative integer representing the total number of periods for the investment.
- `payment` should be a float representing the amount added to the investment each period, which can be zero.
- `present_value` should be a non-negative float representing the initial investment amount.

**Returns:**
`float`: The future value of the investment after the specified number of periods, including contributions and interest earned.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative values for `rate`, `periods`, and `present_value`).
- It then calculates the future value using the formula for future value of a series of cash flows, which incorporates both the present value and the future contributions made at the end of each period.
- The calculation involves applying the compound interest formula to both the present value and the periodic payments, resulting in the total future value.
- This function calls the `financial_svc.calculate_future_value` function to perform the core calculation, leveraging its logic for computing the future value based on the provided parameters.
- If any of the input values are invalid, the function raises a `ValueError` to indicate the issue, ensuring that only valid data is processed. Additionally, it may raise a custom `APIException` to handle errors in a structured manner for API responses.

---
*Generated with 100% context confidence*
