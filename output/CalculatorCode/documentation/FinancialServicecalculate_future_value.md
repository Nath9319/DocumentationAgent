# Documentation for `FinancialService.calculate_future_value`

### calculate_future_value(rate: float, nper: int, pmt: float, pv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the future value of an investment based on periodic contributions and a constant interest rate. This method leverages the `npf.fv` function to determine how much an investment will grow over time, factoring in regular payments and the time value of money.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment.
- `pmt` (`float`): The payment made in each period; it cannot change over the life of the investment.
- `pv` (`float`, optional): The present value, or the initial amount of money before any payments are made. Default is 0.
- `when` (`str`, optional): Indicates when payments are due. It can be 'end' (default) for payments due at the end of the period or 'begin' for payments due at the beginning.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods for the investment.
- `pmt` should be a float representing the payment amount per period, which can be negative if it represents an outgoing payment.
- `pv` should be a float, typically non-negative, representing the initial investment amount.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The future value of the investment after all payments have been made and interest has been applied.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive number of periods).
- It then calls the `npf.fv` function, passing the validated parameters to calculate the future value. This function computes the future value based on the present value, the series of payments, and the interest rate.
- If the `when` parameter is set to 'begin', the calculation adjusts accordingly to account for the timing of the payments.
- The result is computed and returned as a float, representing the total value of the investment at the end of the specified periods. This method relies on the `npf.fv` function for its calculations, ensuring accurate financial computations.

---
*Generated with 100% context confidence*
