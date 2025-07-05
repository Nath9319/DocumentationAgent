# Documentation for FinancialService.calculate_present_value

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### calculate_present_value(future_value: float, annual_rate: float, num_periods: int) -> float

**Description:**
Calculates the present value of an investment based on a specified future value, annual interest rate, and the number of periods until the future value is realized. This method utilizes the net present value formula to determine how much a future sum of money is worth today.

**Parameters:**
- `future_value` (`float`): The amount of money to be received in the future.
- `annual_rate` (`float`): The annual interest rate as a decimal (e.g., 0.05 for 5%).
- `num_periods` (`int`): The total number of periods (years, months, etc.) until the future value is received.

**Expected Input:**
- `future_value` should be a positive float representing the amount expected in the future.
- `annual_rate` should be a non-negative float (0.0 means no interest).
- `num_periods` should be a positive integer indicating the number of periods until the future value is realized.

**Returns:**
`float`: The present value of the future sum of money, representing how much it is worth in today's terms.

**Detailed Logic:**
- The method calls the `npf.pv` function from the external library, which computes the present value based on the provided future value, annual interest rate, and number of periods.
- It applies the formula for present value, which discounts the future cash flow back to the present using the specified interest rate and time frame.
- The result is a single float value that indicates the present worth of the future investment, allowing users to make informed financial decisions based on time value of money principles.

---
*Generated with 0% context confidence*
