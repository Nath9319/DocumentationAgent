### FutureValueInput

**Description:**  
Model for Future Value calculation. Validates cash flow conventions.

**Parameters / Attributes:**  
| Name           | Type   | Description                                   |
|----------------|--------|-----------------------------------------------|
| cash_flows     | list   | List of cash flow amounts for each period.   |
| interest_rate  | float  | The interest rate applied to the cash flows. |
| periods        | int    | Total number of periods for the calculation.  |

**Expected Input:**  
• `cash_flows` must be a list of numeric values.  
• `interest_rate` should be a float representing a percentage (e.g., 0.05 for 5%).  
• `periods` must be a positive integer.

**Returns:**  
`float` – the future value of the cash flows after applying the interest rate over the specified periods.

**Detailed Logic:**  
• Validates the input cash flows to ensure they conform to expected cash flow conventions.  
• Calculates the future value by applying the formula for compound interest to each cash flow based on its timing and the interest rate.  
• Sums the future values of all cash flows to produce the final result.

**Raises / Errors:**  
• Raises a `ValueError` if cash flows are invalid or if the interest rate is negative.  
• Raises a `TypeError` if the input types do not match the expected types.

**Usage Example:**  
```python
fv_input = FutureValueInput(cash_flows=[1000, 2000, 3000], interest_rate=0.05, periods=5)
future_value = fv_input.calculate_future_value()
print(future_value)
```