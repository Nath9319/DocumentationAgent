# Documentation for `calculate_loan_payment`

### calculate_loan_payment(rate: float, num_periods: int, present_value: float) -> float

**Description:**
The `calculate_loan_payment` function serves as an API endpoint that computes the periodic payment required to amortize a loan based on the provided interest rate, number of payment periods, and present value of the loan. This function is essential for users seeking to understand their financial obligations when taking out a loan.

**Parameters:**
- `rate` (`float`): The interest rate per period expressed as a decimal (e.g., 0.05 for 5%).
- `num_periods` (`int`): The total number of payment periods over which the loan will be repaid.
- `present_value` (`float`): The current value of the loan or the amount borrowed.

**Expected Input:**
- `rate` must be a non-negative float, where a value of 0.0 indicates no interest charged.
- `num_periods` should be a positive integer, representing the total number of payments to be made.
- `present_value` must be a positive float, indicating the amount of the loan.

**Returns:**
`float`: The fixed periodic payment amount that must be paid in each period to fully amortize the loan.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive periods, and positive present values).
- It then calls the `financial_svc.calculate_payment` function, passing the `present_value`, `rate`, and `num_periods` as arguments. This function performs the actual calculation of the periodic payment using the net present value formula.
- If any of the input values are invalid, the function raises a `ValueError` to indicate the nature of the issue. Additionally, it may raise a custom `APIException` for handling API-specific errors, ensuring that the response is consistent and informative for the client.
- The result from the `calculate_payment` function is returned as the output, representing the required periodic payment amount.

---
*Generated with 100% context confidence*
