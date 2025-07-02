# Documentation for `FinancialService.calculate_present_value`

### calculate_present_value(rate: float, nper: int, pmt: float, fv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the present value of an investment based on a series of future cash flows. This method utilizes the `npf.pv` function to determine the current worth of an investment or loan by discounting future payments at a specified interest rate.

**Parameters:**
- `rate` (`float`): The interest rate per period expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods.
- `pmt` (`float`): The payment amount made in each period, typically a negative value representing cash outflow.
- `fv` (`float`, optional): The future value or cash balance desired after the last payment. Defaults to 0.
- `when` (`str`, optional): Indicates whether payments are due at the beginning or end of each period. Acceptable values are 'end' (default) and 'begin'.

**Expected Input:**
- `rate` must be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods.
- `pmt` must be a float, typically negative, representing the payment amount.
- `fv` is an optional float that defaults to 0, representing the desired future value.
- `when` should be a string, either 'end' or 'begin', indicating the timing of payments.

**Returns:**
`float`: The present value of the cash flows, which represents the current worth of future payments discounted at the specified interest rate.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they conform to the expected criteria (e.g., non-negative rates, positive periods).
- It then calls the `npf.pv` function, passing the validated parameters to calculate the present value. This function applies the appropriate financial formula to discount future cash flows based on the provided interest rate, number of periods, payment amount, future value, and payment timing.
- If payments are due at the beginning of the period, the calculation is adjusted accordingly to reflect this timing.
- The final computed present value is returned, providing a clear financial metric for evaluating the worth of future cash flows. This method operates solely on the provided parameters and does not have any internal dependencies beyond the `npf.pv` function.

---
*Generated with 100% context confidence*
