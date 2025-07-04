# Documentation for `FinancialService.calculate_future_value`

<<<<<<< HEAD
> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### calculate_future_value(principal: float, annual_rate: float, periods: int) -> float

**Description:**
Calculates the future value of an investment based on the principal amount, the annual interest rate, and the number of periods the investment is held. This method utilizes the net present value formula to determine how much an investment will grow over time, taking into account compound interest.

**Parameters:**
- `principal` (`float`): The initial amount of money invested or loaned.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `periods` (`int`): The total number of compounding periods (e.g., years).

**Expected Input:**
- `principal` should be a positive float representing the initial investment amount.
- `annual_rate` should be a non-negative float (0.0 indicates no interest).
- `periods` should be a non-negative integer representing the number of compounding periods.

**Returns:**
`float`: The future value of the investment after the specified number of periods, including interest.

**Detailed Logic:**
- The method leverages the `npf.fv` function from the external library to compute the future value. This function requires the interest rate per period, the total number of periods, and the principal amount.
- The annual interest rate is converted to a periodic rate by dividing it by the number of compounding periods per year (if applicable).
- The future value is calculated by applying the formula that accounts for compound interest, which considers both the principal and the accumulated interest over the specified periods.
- The result is a float representing the total value of the investment at the end of the specified duration.

---
*Generated with 0% context confidence*
=======
### calculate_future_value(rate: float, nper: int, pmt: float, pv: float = 0, when: str = 'end') -> float

**Description:**
Calculates the future value of an investment or loan based on periodic, constant payments and a constant interest rate. This method is essential for financial analysis, allowing users to determine how much an investment will grow over time given specific parameters.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment or loan.
- `pmt` (`float`): The payment made each period; it cannot change over the life of the investment or loan.
- `pv` (`float`, optional): The present value, or the total amount that a series of future payments is worth now. Defaults to 0 if not provided.
- `when` (`str`, optional): Indicates when payments are due. Acceptable values are 'end' (default) for payments made at the end of each period, and 'begin' for payments made at the beginning of each period.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` must be a positive integer indicating the number of periods.
- `pmt` should be a float representing the payment amount per period, which can be negative if it represents an outgoing payment.
- `pv` is optional and should be a float, typically representing the current value of the investment or loan.
- `when` should be a string that is either 'end' or 'begin', determining the timing of the payments.

**Returns:**
`float`: The future value of the investment or loan after all payments have been made, considering the specified interest rate and payment schedule.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they meet the expected types and constraints.
- It then calls the `npf.fv` function to calculate the future value using the provided parameters: interest rate, number of periods, payment amount, present value, and the timing of payments.
- If payments are made at the beginning of each period, the function adjusts the future value calculation accordingly.
- The final result is computed and returned as a float, representing the total future value of the investment or loan after the specified number of periods.
- This method relies on the `npf.fv` function for its calculations, which performs the necessary arithmetic operations to derive the future value based on the financial parameters provided.

---
*Generated with 100% context confidence*
>>>>>>> f6061b0228250a53c82190181e85a5683699240a
