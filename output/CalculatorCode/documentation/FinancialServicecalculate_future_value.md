# Documentation for `FinancialService.calculate_future_value`

### calculate_future_value(rate: float, nper: int, pmt: float, pv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the future value of an investment based on a constant interest rate, the number of periods, and periodic payments. This method is essential for determining how much an investment will grow over time, considering both the initial investment and any regular contributions made.

**Parameters:**
- `rate` (`float`): The interest rate for each period expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods for the investment.
- `pmt` (`float`): The payment made each period; this amount remains constant throughout the investment's life.
- `pv` (`float`, optional): The present value or initial amount of the investment. Defaults to 0 if not specified.
- `when` (`str`, optional): Specifies when payments are due. Acceptable values are 'end' (default) for payments made at the end of the period, and 'begin' for payments made at the beginning of the period.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the total number of periods.
- `pmt` should be a float representing the payment amount, which can be negative if it indicates an outflow (e.g., an investment).
- `pv` should be a float, typically representing the initial investment amount, and can be zero.
- `when` should be a string that is either 'end' or 'begin', indicating the timing of the payments.

**Returns:**
`float`: The future value of the investment after the specified number of periods, which includes both the initial investment and the total contributions made.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they conform to the expected types and constraints.
- It then calls the `npf.fv` function to compute the future value, utilizing the provided parameters: `rate`, `nper`, `pmt`, `pv`, and `when`.
- The `npf.fv` function applies a financial formula that accounts for the present value, periodic payments, and the interest rate over the specified number of periods.
- If the `when` parameter is set to 'begin', the calculation is adjusted to reflect payments made at the start of each period.
- Finally, the computed future value is returned as a float, representing the total amount the investment will grow to after all contributions and interest have been applied.

---
*Generated with 100% context confidence*
