# Documentation for `FinancialService.calculate_payment`

<<<<<<< HEAD
> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### FinancialService.calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**
The `calculate_payment` method computes the fixed periodic payment required to fully amortize a loan over a specified number of payments. It utilizes the net present value formula to determine the payment amount based on the loan's principal, annual interest rate, and the total number of payments.

**Parameters:**
- `principal` (`float`): The total amount of the loan that needs to be repaid.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**
- `principal` must be a positive float, indicating the loan amount.
- `annual_rate` should be a non-negative float, where a value of 0.0 indicates no interest.
- `num_payments` must be a positive integer, representing the number of payment periods.

**Returns:**
`float`: The fixed payment amount that must be paid in each period to fully amortize the loan.

**Detailed Logic:**
- The method first checks if the `annual_rate` is zero. If it is, the function calculates the payment by dividing the `principal` evenly across all `num_payments`.
- If the `annual_rate` is greater than zero, it converts the annual rate to a monthly interest rate by dividing it by 12.
- The method then applies the standard amortization formula, which incorporates the principal, the monthly interest rate, and the number of payments to compute the periodic payment amount.
- The calculation relies on the `npf.pmt` function from the external library, which simplifies the computation of the payment based on the provided parameters. This function handles the financial calculations internally, ensuring accuracy and efficiency.

---
*Generated with 0% context confidence*
=======
### FinancialService.calculate_payment(rate: float, nper: int, pv: float, fv: float = 0.0, when: str = 'end') -> float

**Description:**
Calculates the periodic payment required to pay off a loan or investment based on a constant interest rate and fixed periodic payments. This method utilizes the `npf.pmt` function to derive the payment amount, making it essential for financial modeling and planning.

**Parameters:**
- `rate` (`float`): The interest rate for each period expressed as a decimal (e.g., 0.05 for 5%).
- `nper` (`int`): The total number of payment periods in the loan or investment.
- `pv` (`float`): The present value, or the total amount of the loan or investment. This can be negative if it represents an outgoing payment.
- `fv` (`float`, optional): The future value, or the cash balance desired after the last payment. Defaults to 0.0.
- `when` (`str`, optional): Indicates when payments are due, either at the 'end' (default) or 'begin' of each period.

**Expected Input:**
- `rate` should be a non-negative float representing the interest rate per period.
- `nper` should be a positive integer indicating the number of payment periods.
- `pv` should be a float representing the present value of the loan or investment.
- `fv` is optional and should be a float, typically 0.0, representing the desired future value.
- `when` should be a string that is either 'end' or 'begin'.

**Returns:**
`float`: The fixed payment amount to be made in each period, calculated based on the provided parameters.

**Detailed Logic:**
- The method begins by validating the input parameters to ensure they conform to the expected criteria (e.g., non-negative rates, positive number of periods).
- It then calls the `npf.pmt` function, passing the validated parameters to compute the periodic payment. This function applies the annuity formula, which considers the present value, future value, interest rate, and number of periods.
- If the `when` parameter is set to 'begin', the payment calculation is adjusted accordingly to account for payments made at the start of each period.
- Finally, the computed payment amount is returned as a float, representing the fixed payment required for the specified loan or investment terms. This method is crucial for users needing to determine payment amounts for various financial scenarios.

---
*Generated with 100% context confidence*
>>>>>>> f6061b0228250a53c82190181e85a5683699240a
