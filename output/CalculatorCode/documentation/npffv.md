# Documentation for `npf.fv`

### npf.fv(rate: float, nper: int, pmt: float, pv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the future value of an investment or loan based on periodic, constant payments and a constant interest rate. This function is essential for financial analysis, allowing users to determine how much an investment will grow over time given specific parameters.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment or loan.
- `pmt` (`float`): The payment made each period; it cannot change over the life of the investment or loan.
- `pv` (`float`, optional): The present value, or the total amount that a series of future payments is worth now. Defaults to 0 if not provided.
- `when` (`str`, optional): Indicates when payments are due. Acceptable values are 'end' (default) for payments made at the end of each period, and 'begin' for payments made at the beginning of each period.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` must be a positive integer indicating the number of periods.
- `pmt` should be a float representing the payment amount per period, which can be negative if it represents an outgoing payment.
- `pv` is optional and should be a float, typically representing the current value of the investment or loan.
- `when` should be a string that is either 'end' or 'begin', determining the timing of the payments.

**Returns:**
`float`: The future value of the investment or loan after all payments have been made, considering the specified interest rate and payment schedule.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected types and constraints.
- It calculates the future value using the formula that incorporates the interest rate, number of periods, payment amount, present value, and the timing of payments.
- If payments are made at the beginning of each period, the function adjusts the future value calculation accordingly.
- The final result is computed and returned as a float, representing the total future value of the investment or loan after the specified number of periods. 
- This function does not rely on any external modules, utilizing basic arithmetic operations to perform its calculations.

---
*Generated with 100% context confidence*
