# Documentation for `get_confidence_interval`

### get_confidence_interval(data: List[float], confidence_level: float) -> Tuple[float, float]

**Description:**
The `get_confidence_interval` function is designed to calculate the confidence interval for a given dataset based on a specified confidence level. This function serves as an API endpoint that accepts sample data and a confidence level, returning a statistical range that likely contains the true population parameter. It leverages the `calculate_confidence_interval` function from the `stats_svc` module to perform the actual computation.

**Parameters:**
- `data` (`List[float]`): A list of numerical values representing the sample data for which the confidence interval is to be calculated.
- `confidence_level` (`float`): A decimal value between 0 and 1 representing the desired confidence level (e.g., 0.95 for a 95% confidence interval).

**Expected Input:**
- `data` should be a non-empty list of floats. The values must be numerical and can include both positive and negative numbers.
- `confidence_level` must be a float in the range (0, 1). Values outside this range will result in an error.

**Returns:**
`Tuple[float, float]`: A tuple containing the lower and upper bounds of the confidence interval.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure that the `data` list is not empty and that the `confidence_level` is within the acceptable range.
- It then calls the `calculate_confidence_interval` function, passing the validated `data` and `confidence_level` as arguments.
- The `calculate_confidence_interval` function computes the sample mean, standard deviation, and critical value based on the t-distribution, ultimately returning the lower and upper bounds of the confidence interval.
- If any errors occur during the calculation (such as invalid input), the function raises an `APIException`, which is a custom exception designed for structured error handling within the API framework.
- This function is registered as a POST request handler using the `router.post` method, allowing it to respond to incoming requests at the specified API endpoint.

---
*Generated with 100% context confidence*
