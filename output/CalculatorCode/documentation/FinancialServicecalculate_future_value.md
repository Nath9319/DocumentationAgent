# Documentation for `FinancialService.calculate_future_value`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### calculate_future_value(principal: float, annual_rate: float, periods: int) -> float

**Description:**
Calculates the future value of an investment based on the principal amount, the annual interest rate, and the number of periods the investment is held. This method utilizes the net present value formula to determine how much an investment will grow over time, taking into account compound interest.

**Parameters:**
- `principal` (`float`): The initial amount of money invested or loaned.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `periods` (`int`): The total number of periods (e.g., years) the money is invested or borrowed for.

**Expected Input:**
- `principal` should be a positive float representing the initial investment amount.
- `annual_rate` should be a non-negative float (0.0 indicates no interest).
- `periods` should be a positive integer representing the number of compounding periods.

**Returns:**
`float`: The future value of the investment after the specified number of periods, including interest.

**Detailed Logic:**
- The method first validates the input parameters to ensure they meet the expected criteria (e.g., non-negative rates and positive integers for periods).
- It then calls the `npf.fv` function from the external library to compute the future value. This function calculates the future value based on the principal, annual interest rate, and the number of compounding periods.
- The result returned by `npf.fv` represents the total amount of money accumulated after the specified time, including interest earned on the principal.

---
*Generated with 0% context confidence*
