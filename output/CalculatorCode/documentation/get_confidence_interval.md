# Documentation for `get_confidence_interval`

```markdown
### get_confidence_interval(data: List[float], confidence_level: float) -> Tuple[float, float]

**Description:**  
Calculates the confidence interval for a given dataset at a specified confidence level. This function is essential for statistical analysis, providing a range within which the true population parameter is expected to lie with a certain level of certainty.

**Parameters:**
- `data` (`List[float]`): A list of numerical values representing the sample data for which the confidence interval is to be calculated.
- `confidence_level` (`float`): A decimal value between 0 and 1 representing the desired confidence level (e.g., 0.95 for a 95% confidence interval).

**Expected Input:**  
- `data` should be a non-empty list of floats, as it represents the sample observations.
- `confidence_level` must be a float in the range (0, 1). Values outside this range will lead to an invalid confidence interval calculation.

**Returns:**  
`Tuple[float, float]`: A tuple containing two float values that represent the lower and upper bounds of the confidence interval.

**Detailed Logic:**  
- The function first checks if the input data is valid, ensuring it is a non-empty list of floats and that the confidence level is within the acceptable range.
- It calculates the sample mean and standard deviation of the provided data.
- Using the standard normal distribution (or t-distribution, depending on the sample size), it determines the critical value corresponding to the specified confidence level.
- Finally, it computes the margin of error and constructs the confidence interval by adding and subtracting this margin from the sample mean.
- If any errors occur during these calculations (e.g., invalid input), the function raises an `APIException` with an appropriate message and status code to ensure consistent error handling across the API.
```