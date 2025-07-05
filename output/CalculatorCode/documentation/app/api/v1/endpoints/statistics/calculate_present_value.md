# Documentation for calculate_present_value

> ⚠️ **Quality Notice**: Documentation generated with 39% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### calculate_present_value(rate: float, nper: int, pmt: float, fv: float) -> float

**Description:**
Calculates the present value of an investment based on the provided rate of return, number of periods, periodic payment, and future value. This function utilizes the financial formula for present value, which discounts future cash flows back to their value today.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment.
- `pmt` (`float`): The payment made in each period; it cannot change over the life of the investment.
- `fv` (`float`): The future value, or a cash balance you want to attain after the last payment is made.

**Expected Input:**
- `rate` should be a non-negative float, representing the interest rate per period.
- `nper` should be a positive integer, indicating the total number of periods for the investment.
- `pmt` can be any float value, representing the periodic payment amount.
- `fv` can also be any float value, representing the desired future value of the investment.

**Returns:**
`float`: The present value of the investment, which represents the current worth of the future cash flows discounted at the specified interest rate.

**Detailed Logic:**
- The function calculates the present value using the financial formula for present value, which is implemented through a call to the `npf.pv` function from the NumPy financial library.
- It takes into account the rate, number of periods, periodic payment, and future value to compute the present value.
- The result is a single float value that indicates how much a series of future cash flows is worth today, given the specified parameters. This function does not handle exceptions directly but relies on the underlying financial calculations, which may raise errors (e.g., `ValueError`) if the inputs are invalid.

---
*Generated with 39% context confidence*
