# Documentation for `FinancialService.calculate_payment`

### calculate_payment(rate: float, nper: int, pv: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the fixed periodic payment required to repay a loan or achieve a future value (FV) based on the present value (PV), interest rate, and number of payment periods. This method utilizes the `npf.pmt` function to derive the payment amount, making it essential for financial calculations related to loans and investments.

**Parameters:**
- `rate` (`float`): The interest rate for each period expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods (must be a positive integer).
- `pv` (`float`): The present value or principal amount, which can be negative if it represents an outgoing payment (e.g., a loan).
- `fv` (`float`, optional): The desired future value at the end of the payment periods. Defaults to 0.0.
- `when` (`str`, optional): Specifies when payments are due. Acceptable values are 'end' (payments due at the end of the period) and 'begin' (payments due at the beginning of the period). Defaults to 'end'.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods.
- `pv` should be a float representing the present value, which can be negative if it represents an outgoing payment.
- `fv` should be a float representing the future value, which can also be negative if it represents an outgoing payment.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The fixed payment amount to be made in each period to reach the specified future value.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they conform to the expected criteria (e.g., non-negative rates, positive number of periods).
- It then calls the `npf.pmt` function, passing the validated parameters to calculate the periodic payment. This function applies the present value of an annuity formula, which incorporates the interest rate, number of periods, present value, and future value.
- Depending on the value of the `when` parameter, the method adjusts the calculation to account for whether payments are made at the beginning or the end of each period.
- The method does not rely on any external modules beyond the `npf` library and performs calculations using basic arithmetic operations.

---
*Generated with 100% context confidence*
