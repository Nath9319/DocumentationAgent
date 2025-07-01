# Documentation for `StatsService.calculate_confidence_interval`

```markdown
### calculate_confidence_interval(data: List[float], confidence_level: float) -> Tuple[float, float]

**Description:**  
Calculates the confidence interval for a given list of numerical data, providing a range within which the true population parameter is expected to lie with a specified level of confidence.

**Parameters:**
- `data` (`List[float]`): A list of numerical values for which the confidence interval is to be calculated.
- `confidence_level` (`float`): A value between 0 and 1 representing the desired confidence level (e.g., 0.95 for a 95% confidence interval).

**Expected Input:**  
- `data` should be a non-empty list of floats, representing sample observations. The list must contain at least two elements to compute a valid confidence interval.
- `confidence_level` must be a float in the range (0, 1). Values outside this range will lead to invalid calculations.

**Returns:**  
`Tuple[float, float]`: A tuple containing two floats that represent the lower and upper bounds of the confidence interval.

**Detailed Logic:**  
- The function begins by validating the input parameters to ensure that the data list is non-empty and that the confidence level is within the acceptable range.
- It calculates the sample mean and standard deviation of the provided data.
- Using the standard error of the mean, it determines the critical value from the appropriate statistical distribution based on the specified confidence level.
- Finally, it computes the lower and upper bounds of the confidence interval by adjusting the sample mean with the critical value multiplied by the standard error.
- The function returns the calculated bounds as a tuple, providing a clear indication of the range within which the true population mean is likely to fall.
```