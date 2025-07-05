# Documentation for get_z_scores

> ⚠️ **Quality Notice**: Documentation generated with 48% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### get_z_scores(data: List[float]) -> List[float]

**Description:**
The `get_z_scores` function computes the Z-scores for a given list of numerical data. Z-scores indicate how many standard deviations an element is from the mean of the dataset, providing a standardized way to understand the relative position of each data point within the distribution.

**Parameters:**
- `data` (`List[float]`): A list of floating-point numbers for which the Z-scores will be calculated.

**Expected Input:**
- `data` should be a non-empty list of numerical values (floats). The list must contain valid numbers to ensure accurate calculations of the mean and standard deviation. If the list is empty or contains non-numeric values, the function may raise an exception.

**Returns:**
`List[float]`: A list of Z-scores corresponding to each element in the input list. Each Z-score is a floating-point number representing the number of standard deviations away from the mean.

**Detailed Logic:**
- The function first checks the validity of the input data to ensure it is a non-empty list of numbers.
- It then calculates the mean and standard deviation of the input data using the `calculate_z_scores` method from the `StatsService` class.
- Each Z-score is computed by subtracting the mean from each data point and dividing the result by the standard deviation.
- The function returns a list of Z-scores rounded to four decimal places, providing a clear representation of how each data point relates to the overall distribution. 
- If any errors occur during the calculation (e.g., division by zero if the standard deviation is zero), the function may raise an `APIException` to handle the error gracefully and return a structured error message to the client.

---
*Generated with 48% context confidence*
