# Documentation for `FinancialService.calculate_present_value`

### calculate_present_value(rate: float, nper: int, pmt: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the present value of an investment based on a series of future cash flows, discounted at a specified interest rate. This method is essential for financial analysis, allowing users to determine the current worth of future payments or cash inflows.

**Parameters:**
- `rate` (`float`): The interest rate for each period, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the investment or loan.
- `pmt` (`float`): The payment made in each period; it cannot change over the life of the investment or loan.
- `fv` (`float`, optional): The future value, or a cash balance you want to attain after the last payment is made. Default is 0.0.
- `when` (`str`, optional): Indicates when payments are due. Can be 'end' (default) for payments at the end of the period or 'begin' for payments at the beginning.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of periods.
- `pmt` should be a float representing the payment amount per period, which can be negative if it represents an outgoing payment.
- `fv` should be a float, typically set to 0.0 unless a specific future value is desired.
- `when` should be a string, either 'end' or 'begin', to specify the timing of payments.

**Returns:**
`float`: The present value of the cash flows, representing the current worth of future payments discounted at the specified interest rate.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they meet the expected types and constraints.
- It then calls the `npf.pv` function, which performs the core calculation of the present value using the provided parameters: interest rate, number of periods, payment amount, future value, and timing of payments.
- If the `when` parameter is set to 'begin', the method adjusts the present value calculation to account for the earlier timing of payments.
- The final present value is computed and returned, providing a clear financial metric for decision-making. This method leverages the functionality of the `npf.pv` function to perform the necessary calculations efficiently.

---
*Generated with 100% context confidence*
