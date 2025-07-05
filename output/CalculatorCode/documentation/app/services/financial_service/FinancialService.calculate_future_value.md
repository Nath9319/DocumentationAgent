# Documentation for FinancialService.calculate_future_value

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### calculate_future_value(principal: float, annual_rate: float, periods: int) -> float

**Description:**
Calculates the future value of an investment based on the initial principal, the annual interest rate, and the number of periods the investment is held. This method utilizes the net present value formula to compute the future worth of the investment at the end of the specified periods.

**Parameters:**
- `principal` (`float`): The initial amount of money invested or loaned.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `periods` (`int`): The total number of periods (e.g., years) the money is invested or borrowed.

**Expected Input:**
- `principal` should be a positive float representing the initial investment amount.
- `annual_rate` should be a non-negative float; a value of 0.0 indicates no interest will accrue.
- `periods` should be a positive integer representing the number of periods the investment will grow.

**Returns:**
`float`: The future value of the investment after the specified number of periods, taking into account the principal and the interest accrued.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates and positive integers for periods).
- It then calls the `npf.fv` function from the external library, which computes the future value based on the provided principal, annual interest rate, and the number of periods.
- The `npf.fv` function applies the formula for future value, which considers compound interest, and returns the calculated future value.
- Finally, the method returns this computed future value, allowing users to understand the potential growth of their investment over time.

---
*Generated with 0% context confidence*
