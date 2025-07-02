# Documentation for `get_z_scores`

### get_z_scores(data: List[float]) -> List[float]

**Description:**
The `get_z_scores` function is designed to compute the z-scores for a given dataset. A z-score quantifies the number of standard deviations a data point is from the mean of the dataset, thereby providing insight into the relative position of each data point within the distribution. This function is typically used in statistical analysis to identify outliers or to standardize data for further processing.

**Parameters:**
- `data` (`List[float]`): A list of numerical values for which the z-scores will be calculated.

**Expected Input:**
- `data` should be a non-empty list containing floats or integers. The values can be positive, negative, or zero, but the list must contain at least one element to compute the mean and standard deviation.

**Returns:**
`List[float]`: A list of z-scores corresponding to the input data, where each z-score indicates how many standard deviations a data point is from the mean.

**Detailed Logic:**
- The function begins by validating the input to ensure that the `data` list is non-empty.
- It then calculates the mean of the dataset by summing all the values and dividing by the number of values.
- Following this, the standard deviation is computed, which involves calculating the variance (the average of the squared differences from the mean) and taking the square root of that variance.
- For each value in the dataset, the z-score is calculated using the formula: \( z = \frac{(X - \text{mean})}{\text{std\_dev}} \), where \( X \) is the individual data point.
- The resulting z-scores are collected into a list and returned to the caller.
- This function relies on the `stats_svc.calculate_z_scores` method to perform the actual z-score calculations, ensuring that the logic is encapsulated and reusable.

---
*Generated with 100% context confidence*
