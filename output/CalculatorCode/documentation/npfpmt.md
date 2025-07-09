# Documentation for `npf.pmt`

### npf.pmt(rate: float, nper: int, pv: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the fixed periodic payment required to repay a loan or investment over a specified number of periods, taking into account the interest rate, present value, future value, and the timing of payments.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the loan or investment.
- `pv` (`float`): The present value, or the total amount that a series of future payments is worth now.
- `fv` (`float`, optional): The future value, or a cash balance you want to attain after the last payment is made. Defaults to 0.0.
- `when` (`str`, optional): Specifies when payments are due. Can be 'end' (default) for payments at the end of the period or 'begin' for payments at the beginning.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the total number of payment periods.
- `pv` should be a float representing the present value, which can be negative if it represents an outgoing payment (like a loan).
- `fv` is optional and defaults to 0.0, indicating no future value unless specified.
- `when` should be either 'end' or 'begin', with 'end' being the default.

**Returns:**
`float`: The fixed payment amount to be made in each period, which can be positive or negative depending on the cash flow direction.

**Detailed Logic:**
- The function first validates the input parameters to ensure they meet the expected types and constraints.
- It calculates the periodic payment using the formula derived from the annuity formula, which accounts for the present value, future value, interest rate, and number of periods.
- If the interest rate is zero, the function simplifies the calculation to evenly distribute the present value over the number of periods.
- The function also considers the timing of payments (beginning or end of the period) to adjust the final payment amount accordingly.
- The result is computed and returned as a float, representing the fixed payment amount required for the specified loan or investment scenario.

---
*Generated with 100% context confidence*
