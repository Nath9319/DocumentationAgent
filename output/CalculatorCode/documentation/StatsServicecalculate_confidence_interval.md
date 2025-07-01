# Documentation for `StatsService.calculate_confidence_interval`

### calculate_confidence_interval(data: List[float], confidence_level: float) -> Tuple[float, float]

**Description:**
Calculates the confidence interval for a given list of numerical data points. The confidence interval provides a range within which the true population parameter (e.g., mean) is expected to lie, with a specified level of confidence.

**Parameters:**
- `data` (`List[float]`): A list of numerical values for which the confidence interval is to be calculated.
- `confidence_level` (`float`): The desired confidence level for the interval, expressed as a decimal (e.g., 0.95 for a 95% confidence interval).

**Expected Input:**
- `data` should be a non-empty list of floats or integers. The list must contain at least two elements to compute a meaningful confidence interval.
- `confidence_level` should be a float between 0 and 1, representing the desired confidence level. Values outside this range will result in an error.

**Returns:**
`Tuple[float, float]`: A tuple containing two float values that represent the lower and upper bounds of the confidence interval.

**Detailed Logic:**
- The function first calculates the sample mean of the provided data using the `np.mean` function from the NumPy library.
- It then determines the standard error of the mean using the `st.sem` function from the SciPy library, which computes the standard deviation of the sample divided by the square root of the sample size.
- Next, the function uses the `st.t.ppf` function from SciPy to find the critical t-value based on the specified confidence level and the degrees of freedom (which is the sample size minus one).
- Finally, it computes the margin of error by multiplying the standard error by the critical t-value, and constructs the confidence interval by adding and subtracting this margin from the sample mean.
- The resulting lower and upper bounds of the confidence interval are returned as a tuple.