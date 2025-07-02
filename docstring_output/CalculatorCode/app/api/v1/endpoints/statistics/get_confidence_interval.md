### get_confidence_interval(data: list, confidence_level: float) -> tuple

**Description:**  
Calculates the confidence interval for a given dataset at a specified confidence level, providing a range within which the true population parameter is expected to lie.

**Parameters:**  
| Name            | Type   | Description                                           |
|-----------------|--------|-------------------------------------------------------|
| data            | list   | A list of numerical values representing the sample data. |
| confidence_level| float  | The confidence level for the interval (e.g., 0.95 for 95% confidence). |

**Expected Input:**  
• `data` must be a non-empty list of numerical values.  
• `confidence_level` should be between 0 and 1 (exclusive).

**Returns:**  
`tuple` – A tuple containing two float values representing the lower and upper bounds of the confidence interval.

**Detailed Logic:**  
• Validates the input data to ensure it is a non-empty list of numbers.  
• Computes the sample mean and standard error of the mean.  
• Uses the appropriate statistical distribution (e.g., t-distribution for small samples) to determine the critical value based on the specified confidence level.  
• Calculates the margin of error by multiplying the critical value by the standard error.  
• Constructs the confidence interval by subtracting and adding the margin of error from the sample mean.

**Raises / Errors:**  
• Raises `ValueError` if `data` is empty or if `confidence_level` is not between 0 and 1.  
• Raises `TypeError` if `data` contains non-numeric values.

**Usage Example:**  
```python
data = [12, 15, 14, 10, 13, 16, 14]
confidence_level = 0.95
interval = get_confidence_interval(data, confidence_level)
print(interval)  # Output might be (lower_bound, upper_bound)
```