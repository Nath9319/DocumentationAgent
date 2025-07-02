# Documentation for `get_z_scores`

> ⚠️ **Quality Notice**: Documentation generated with 48% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### get_z_scores(data: List[float]) -> List[float]

**Description:**
The `get_z_scores` function calculates the Z-scores for a given list of numerical data. Z-scores indicate how many standard deviations an element is from the mean of the dataset, providing a way to understand the relative position of each data point within the distribution.

**Parameters:**
- `data` (`List[float]`): A list of floating-point numbers for which the Z-scores will be calculated.

**Expected Input:**
- The `data` parameter should be a non-empty list of floats. It is important that the list contains numerical values to ensure valid calculations. If the list is empty or contains non-numeric values, the function may raise an exception.

**Returns:**
`List[float]`: A list of Z-scores corresponding to the input data. Each Z-score represents the number of standard deviations a data point is from the mean of the dataset.

**Detailed Logic:**
- The function begins by validating the input data to ensure it is a non-empty list of floats.
- It then calculates the mean and standard deviation of the input data using the `calculate_z_scores` method from the `StatsService` class.
- The Z-scores are computed using the formula: \( Z = \frac{(X - \text{mean})}{\text{std\_dev}} \), where \( X \) is each individual data point.
- The results are rounded to four decimal places for precision and returned as a list.
- If any errors occur during the calculation (e.g., division by zero if the standard deviation is zero), the function raises an `APIException` to provide structured error handling, ensuring that the API can return a well-formed JSON error message to the client.

---
*Generated with 48% context confidence*
