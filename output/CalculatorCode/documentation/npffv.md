# Documentation for `npf.fv`

### npf.fv(rate: float, nper: int, pmt: float, pv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the future value of an investment based on a constant interest rate, the number of periods, periodic payments, and an optional present value. This function is useful for financial calculations where one needs to determine how much an investment will grow over time with regular contributions.

**Parameters:**
- `rate` (`float`): The interest rate for each period as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment.
- `pmt` (`float`): The payment made each period; it cannot change over the life of the investment.
- `pv` (`float`, optional): The present value or initial amount of the investment. Defaults to 0 if not provided.
- `when` (`str`, optional): Indicates when payments are due. Acceptable values are 'end' (default) for payments made at the end of the period, and 'begin' for payments made at the beginning of the period.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods.
- `pmt` should be a float representing the payment amount, which can be negative if it represents an outflow.
- `pv` should be a float, typically representing the initial investment amount, and can be zero.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The future value of the investment after the specified number of periods, including both the initial investment and the total contributions made.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected types and constraints.
- It calculates the future value using the formula that incorporates the present value, periodic payments, and the interest rate over the specified number of periods.
- If `when` is set to 'begin', the function adjusts the calculation to account for payments made at the start of each period.
- The final result is computed and returned as a float, representing the total future value of the investment after all contributions and interest have been applied.
- This function does not rely on any external dependencies and utilizes basic arithmetic operations to perform its calculations.

---
*Generated with 100% context confidence*
