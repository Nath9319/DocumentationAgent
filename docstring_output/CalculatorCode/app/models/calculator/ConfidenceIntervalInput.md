### ConfidenceIntervalInput

**Description:**  
Model for Confidence Interval calculation.

**Parameters:**  
| Name       | Type   | Description                           |
|------------|--------|---------------------------------------|
| data       | list   | A list of numerical values for which the confidence interval is to be calculated. |
| confidence  | float  | The confidence level for the interval, typically between 0 and 1 (e.g., 0.95 for 95% confidence). |

**Expected Input:**  
• `data` must be a non-empty list of numerical values.  
• `confidence` should be a float value in the range (0, 1).

**Returns:**  
`tuple` – A tuple containing the lower and upper bounds of the confidence interval.

**Detailed Logic:**  
• The model calculates the mean and standard deviation of the provided data.  
• It determines the appropriate z-score or t-score based on the specified confidence level and sample size.  
• The confidence interval is then computed using the formula:  
  - Lower Bound = Mean - (Critical Value * Standard Error)  
  - Upper Bound = Mean + (Critical Value * Standard Error)  
• The result is returned as a tuple containing the lower and upper bounds of the confidence interval.

**Raises / Errors:**  
• Raises `ValueError` if `data` is empty or if `confidence` is not in the range (0, 1).  
• Raises `TypeError` if `data` contains non-numeric values.

**Usage Example:**  
```python
ci_input = ConfidenceIntervalInput(data=[1, 2, 3, 4, 5], confidence=0.95)
confidence_interval = ci_input.calculate()
print(confidence_interval)  # Output: (lower_bound, upper_bound)
```