# Documentation for `npf.pmt`

### npf.pmt(rate: float, nper: int, pv: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the fixed periodic payment required to pay off a loan or investment based on constant periodic payments and a constant interest rate. This function is commonly used in financial calculations to determine the payment amount for loans or annuities.

**Parameters:**
- `rate` (`float`): The interest rate for each period. This should be expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the loan or investment.
- `pv` (`float`): The present value, or the total amount of the loan or investment.
- `fv` (`float`, optional): The future value, or the cash balance you want to attain after the last payment is made. Defaults to 0.0.
- `when` (`str`, optional): Specifies whether payments are due at the beginning or end of each period. Acceptable values are 'end' (default) and 'begin'.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of payment periods.
- `pv` should be a float representing the present value of the loan or investment, which can be negative if it represents an outgoing payment.
- `fv` is optional and should be a float, typically 0.0, representing the desired future value.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The fixed payment amount to be made in each period.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive number of periods).
- It calculates the periodic payment using the formula derived from the annuity formula, which considers the present value, future value, interest rate, and number of periods.
- If the `when` parameter is set to 'begin', the function adjusts the payment calculation to account for payments made at the start of each period.
- The final computed payment amount is returned as a float, representing the fixed payment required for the specified loan or investment terms. 

This function is essential for financial modeling and planning, allowing users to easily compute payment amounts for various loan scenarios.

---
*Generated with 100% context confidence*
