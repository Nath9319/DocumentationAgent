# Documentation for calculate_loan_payment

> ⚠️ **Quality Notice**: Documentation generated with 38% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### calculate_loan_payment(rate: float, nper: int, pv: float) -> float

**Description:**
The `calculate_loan_payment` function computes the periodic payment required to repay a loan based on the specified interest rate, number of payment periods, and present value of the loan. It serves as an endpoint for clients to determine their loan payment obligations.

**Parameters:**
- `rate` (`float`): The interest rate for the loan, expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods over which the loan will be repaid.
- `pv` (`float`): The present value or principal amount of the loan.

**Expected Input:**
- `rate` should be a non-negative float. A value of 0 indicates a zero-interest loan.
- `nper` should be a positive integer representing the total number of payments.
- `pv` should be a positive float representing the loan amount.

**Returns:**
`float`: The calculated periodic payment amount that the borrower must pay in each period to fully amortize the loan.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they meet the expected criteria (e.g., non-negative rates, positive number of periods, and positive present value).
- It then utilizes the `calculate_payment` method from the `FinancialService` class, which employs the net present value formula to determine the periodic payment based on the provided inputs.
- If any errors occur during the calculation (such as invalid input types), the function raises an `APIException` with an appropriate status code and error message, ensuring that clients receive structured feedback on their requests.

---
*Generated with 38% context confidence*
