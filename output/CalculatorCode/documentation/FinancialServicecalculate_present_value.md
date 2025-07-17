# Documentation for `FinancialService.calculate_present_value`

### calculate_present_value(rate: float, nper: int, pmt: float, fv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the present value of an investment based on a series of future cash flows. This method utilizes the `npf.pv` function to determine the current worth of an investment or loan given specified parameters such as interest rate, number of periods, payment amount, future value, and timing of payments.

**Parameters:**
- `rate` (`float`): The interest rate per period expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment or loan.
- `pmt` (`float`): The payment made each period; this value remains constant throughout the investment or loan duration.
- `fv` (`float`, optional): The future value or cash balance desired after the last payment. Defaults to 0 if not specified.
- `when` (`str`, optional): Specifies when payments are due, either 'end' (default) for payments made at the end of the period or 'begin' for payments made at the beginning.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the total number of payment periods.
- `pmt` should be a float representing the payment amount, which can be negative (indicating cash outflow).
- `fv` is optional and can be any float, typically set to 0 if not specified.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The present value of the series of future cash flows, representing the current worth of the investment or loan.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they conform to the expected criteria (e.g., non-negative rates, positive number of periods).
- It then calls the `npf.pv` function, passing the validated parameters to compute the present value. The function uses the specified interest rate, number of periods, payment amount, future value, and timing of payments to perform the calculation.
- If the `when` parameter is set to 'begin', the calculation adjusts accordingly to reflect payments made at the start of each period.
- The final result is computed and returned as a float, representing the present value of the cash flows. This method effectively encapsulates the financial calculation logic while relying on the external `npf.pv` function for the core computation.

---
*Generated with 100% context confidence*
