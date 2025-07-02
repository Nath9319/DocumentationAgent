# Documentation for `npf.pv`

### npf.pv(rate: float, nper: int, pmt: float, fv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the present value of a series of future cash flows, given a specified interest rate, number of periods, and payment amount. This function is commonly used in finance to determine the current worth of an investment or loan based on expected future payments.

**Parameters:**
- `rate` (`float`): The interest rate per period as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods.
- `pmt` (`float`): The payment amount made in each period. This value should be negative if it represents cash outflow.
- `fv` (`float`, optional): The future value or cash balance you want to attain after the last payment is made. Defaults to 0.
- `when` (`str`, optional): Specifies whether payments are due at the beginning or end of each period. Acceptable values are 'end' (default) and 'begin'.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods.
- `pmt` should be a float, typically negative, representing the payment amount.
- `fv` is an optional float that defaults to 0, representing the desired future value.
- `when` should be a string, either 'end' or 'begin', indicating the timing of payments.

**Returns:**
`float`: The present value of the cash flows, representing the current worth of future payments discounted at the specified interest rate.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive periods).
- It calculates the present value using the formula that incorporates the interest rate, number of periods, payment amount, future value, and the timing of payments.
- If payments are due at the beginning of the period, the function adjusts the calculation accordingly.
- The final present value is computed and returned, providing a clear financial metric for evaluating the worth of future cash flows. 

This function does not have any internal dependencies and operates solely on the provided parameters, utilizing basic arithmetic operations to derive the present value.

---
*Generated with 100% context confidence*
