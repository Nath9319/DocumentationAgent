# Documentation for `calculate_loan_payment`

### calculate_loan_payment(rate: float, num_periods: int, present_value: float) -> float

**Description:**
The `calculate_loan_payment` function serves as an endpoint for calculating the periodic payment required to repay a loan based on the provided interest rate, number of payment periods, and present value of the loan. It leverages the `calculate_payment` function from the `financial_svc` module to perform the actual payment calculation.

**Parameters:**
- `rate` (`float`): The interest rate for the loan, expressed as a decimal (e.g., 0.05 for 5%).
- `num_periods` (`int`): The total number of payment periods (e.g., months or years) over which the loan will be repaid.
- `present_value` (`float`): The current value of the loan, representing the total amount borrowed.

**Expected Input:**
- `rate` must be a non-negative float, where a value of 0.0 indicates that there is no interest charged on the loan.
- `num_periods` must be a positive integer, indicating the total number of payments to be made.
- `present_value` should be a positive float, representing the loan amount that needs to be repaid.

**Returns:**
`float`: The fixed periodic payment amount that must be paid in each period to fully amortize the loan by the end of the specified number of payments.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive periods, and present values).
- It then calls the `calculate_payment` function, passing the `present_value`, `rate`, and `num_periods` as arguments to compute the required periodic payment.
- If any of the input parameters are invalid, the function raises a `ValueError` to indicate the nature of the input issue.
- The result from the `calculate_payment` function is returned as the output, representing the calculated loan payment amount. This function is designed to be used as part of a web API, responding to POST requests with the calculated payment information.

---
*Generated with 100% context confidence*
