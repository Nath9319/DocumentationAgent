# Documentation for calculate_future_value

> ⚠️ **Quality Notice**: Documentation generated with 39% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### calculate_future_value(rate: float, nper: int, pmt: float, pv: float) -> float

**Description:**
Calculates the future value of an investment based on a specified interest rate, number of periods, periodic payment, and present value. This function utilizes the financial formula for future value, which accounts for compound interest and periodic contributions.

**Parameters:**
- `rate` (`float`): The interest rate per period as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment.
- `pmt` (`float`): The payment made each period; it can be a positive or negative value depending on whether it is an inflow or outflow.
- `pv` (`float`): The present value or initial amount of the investment.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods for the investment.
- `pmt` can be any float value, representing the amount paid or received in each period.
- `pv` should be a float representing the current value of the investment, which can also be negative if it represents debt.

**Returns:**
`float`: The future value of the investment after the specified number of periods, accounting for the interest rate and periodic payments.

**Detailed Logic:**
- The function calls an external financial service method to perform the calculation of future value using the provided parameters.
- It applies the future value formula, which incorporates the interest rate, number of periods, periodic payments, and present value to compute the total future value of the investment.
- The calculation is based on the principles of compound interest, where the future value is determined by both the growth of the present value and the contributions made over time.

---
*Generated with 39% context confidence*
