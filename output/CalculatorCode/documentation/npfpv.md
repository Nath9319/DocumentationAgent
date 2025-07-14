# Documentation for `npf.pv`

### npf.pv(rate: float, nper: int, pmt: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the present value of a series of future cash flows based on a specified interest rate. This function is commonly used in financial analysis to determine the current worth of an investment or loan, given a series of future payments.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment or loan.
- `pmt` (`float`): The payment made in each period; it cannot change over the life of the investment or loan.
- `fv` (`float`, optional): The future value, or a cash balance you want to attain after the last payment is made. Default is 0.0.
- `when` (`str`, optional): Indicates when payments are due. Can be 'end' (default) for payments at the end of the period or 'begin' for payments at the beginning.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods.
- `pmt` should be a float representing the payment amount per period, which can be negative if it represents an outgoing payment.
- `fv` should be a float, typically set to 0.0 unless a specific future value is desired.
- `when` should be a string, either 'end' or 'begin', to specify the timing of payments.

**Returns:**
`float`: The present value of the cash flows, representing the current worth of future payments discounted at the specified interest rate.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected types and constraints.
- It calculates the present value using the formula that incorporates the interest rate, number of periods, payment amount, future value, and timing of payments.
- If `when` is set to 'begin', the function adjusts the present value calculation to account for the earlier timing of payments.
- The final present value is computed and returned, providing a clear financial metric for decision-making. This function does not rely on any external modules, utilizing basic arithmetic operations to derive the present value.

---
*Generated with 100% context confidence*
