# Documentation for `npf.pmt`

### npf.pmt(rate: float, nper: int, pv: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the fixed periodic payment required to achieve a future value (FV) given a present value (PV), a specified interest rate, and the number of periods (nper). This function is commonly used in financial calculations to determine loan payments or investment contributions.

**Parameters:**
- `rate` (`float`): The interest rate for each period as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods.
- `pv` (`float`): The present value or principal amount (the initial amount of money).
- `fv` (`float`, optional): The future value or the desired amount of money at the end of the payment periods. Defaults to 0.0.
- `when` (`str`, optional): Indicates when payments are due. Acceptable values are 'end' (payments due at the end of the period) and 'begin' (payments due at the beginning of the period). Defaults to 'end'.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods.
- `pv` should be a float representing the present value, which can be negative if it represents an outgoing payment (like a loan).
- `fv` should be a float representing the future value, which can also be negative if it represents an outgoing payment.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The fixed payment amount to be made in each period to reach the specified future value.

**Detailed Logic:**
- The function first validates the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive number of periods).
- It calculates the periodic payment using the formula derived from the present value of an annuity formula, which incorporates the interest rate, number of periods, present value, and future value.
- Depending on the value of the `when` parameter, the function adjusts the calculation to account for whether payments are made at the beginning or the end of each period.
- The function does not rely on any external modules and performs calculations using basic arithmetic operations.

---
*Generated with 100% context confidence*
