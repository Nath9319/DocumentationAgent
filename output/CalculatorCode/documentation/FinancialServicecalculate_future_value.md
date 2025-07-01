# Documentation for `FinancialService.calculate_future_value`

### calculate_future_value(principal: float, annual_rate: float, periods: int) -> float

**Description:**
Calculates the future value of an investment based on the principal amount, the annual interest rate, and the number of periods the investment is held. This method utilizes the future value formula, which accounts for compound interest over the specified periods.

**Parameters:**
- `principal` (`float`): The initial amount of money invested or loaned.
- `annual_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `periods` (`int`): The total number of compounding periods (e.g., years) the money is invested or borrowed.

**Expected Input:**
- `principal` should be a positive float representing the initial investment amount.
- `annual_rate` should be a non-negative float (0.0 indicates no interest).
- `periods` should be a non-negative integer representing the number of periods for compounding.

**Returns:**
`float`: The future value of the investment after the specified number of periods, including interest.

**Detailed Logic:**
- The method first validates the input parameters to ensure they meet the expected criteria (e.g., non-negative values for `annual_rate` and `periods`, and a positive value for `principal`).
- It then calls the `npf.fv` function from the NumPy Financial library, which computes the future value based on the provided principal, annual interest rate, and number of periods.
- The `npf.fv` function applies the formula for compound interest, effectively calculating how much the initial investment will grow over time given the specified interest rate and compounding periods.
- The result is returned as a float, representing the total amount accumulated after interest has been applied.