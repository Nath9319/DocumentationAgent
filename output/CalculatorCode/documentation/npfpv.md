# Documentation for `npf.pv`

### npf.pv(rate: float, nper: int, pmt: float, fv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the present value of a series of future cash flows based on a specified interest rate, number of periods, payment amount, future value, and timing of payments. This function is commonly used in financial calculations to determine the current worth of an investment or loan given future cash flows.

**Parameters:**
- `rate` (`float`): The interest rate per period as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment or loan.
- `pmt` (`float`): The payment made each period; it cannot change over the life of the investment or loan.
- `fv` (`float`, optional): The future value, or a cash balance you want to attain after the last payment is made. Defaults to 0.
- `when` (`str`, optional): Indicates when payments are due. It can be 'end' (default) for payments at the end of the period or 'begin' for payments at the beginning of the period.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer representing the total number of payment periods.
- `pmt` should be a float that represents the payment amount, which can be negative (indicating cash outflow).
- `fv` is optional and can be any float, typically set to 0 if not specified.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The present value of the series of future cash flows, representing the current worth of the investment or loan.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive number of periods).
- It calculates the present value using the formula that incorporates the interest rate, number of periods, payment amount, future value, and timing of payments.
- If `when` is set to 'begin', the function adjusts the calculation to account for payments made at the start of each period.
- The final result is computed and returned as a float, representing the present value of the cash flows. This function does not rely on any external dependencies and uses basic arithmetic operations to perform the calculations.

---
*Generated with 100% context confidence*
