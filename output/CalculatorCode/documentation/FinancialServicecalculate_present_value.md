# Documentation for `FinancialService.calculate_present_value`

### calculate_present_value(rate: float, nper: int, pmt: float, fv: float, when: str) -> float

**Description:**
Calculates the present value of an investment based on a specified interest rate, number of periods, periodic payment, future value, and the timing of the payment. This method is essential for financial analysis, allowing users to determine the current worth of future cash flows.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment's lifespan.
- `pmt` (`float`): The amount of money paid or received in each period.
- `fv` (`float`): The future value of the investment at the end of the last period.
- `when` (`str`): Indicates when payments are due. Acceptable values are 'end' (default) for payments made at the end of each period or 'begin' for payments made at the beginning.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the total number of periods.
- `pmt` can be any float value, representing the payment amount per period.
- `fv` should be a float representing the future value of the investment.
- `when` should be a string that is either 'begin' or 'end', indicating the timing of the payments.

**Returns:**
`float`: The present value of the investment, representing the current worth of future cash flows discounted at the specified interest rate.

**Detailed Logic:**
- The method utilizes the `npf.pv` function from the NumPy Financial library to perform the present value calculation.
- It first prepares the input parameters, ensuring they conform to the expected types and values.
- The `npf.pv` function is called with the provided parameters, which computes the present value based on the formula for discounting future cash flows.
- The result is then returned as a float, representing the present value of the investment based on the specified criteria. This method effectively abstracts the complexity of the underlying financial calculations, providing a straightforward interface for users.