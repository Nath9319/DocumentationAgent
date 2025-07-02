# Documentation for `FinancialService.calculate_payment`

### FinancialService.calculate_payment(rate: float, nper: int, pv: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the periodic payment required to pay off a loan or investment based on a constant interest rate and fixed periodic payments. This method utilizes the `npf.pmt` function to derive the payment amount, making it essential for financial modeling and planning.

**Parameters:**
- `rate` (`float`): The interest rate for each period expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the loan or investment.
- `pv` (`float`): The present value, or the total amount of the loan or investment. This can be negative if it represents an outgoing payment.
- `fv` (`float`, optional): The future value, or the cash balance desired after the last payment. Defaults to 0.0.
- `when` (`str`, optional): Indicates when payments are due, either at the 'end' (default) or 'begin' of each period.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of payment periods.
- `pv` should be a float representing the present value of the loan or investment.
- `fv` is optional and should be a float, typically 0.0, representing the desired future value.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The fixed payment amount to be made in each period, calculated based on the provided parameters.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they conform to the expected criteria (e.g., non-negative rates, positive number of periods).
- It then calls the `npf.pmt` function, passing the validated parameters to compute the periodic payment. This function applies the annuity formula, which considers the present value, future value, interest rate, and number of periods.
- If the `when` parameter is set to 'begin', the payment calculation is adjusted accordingly to account for payments made at the start of each period.
- Finally, the computed payment amount is returned as a float, representing the fixed payment required for the specified loan or investment terms. This method is crucial for users needing to determine payment amounts for various financial scenarios.

---
*Generated with 100% context confidence*
