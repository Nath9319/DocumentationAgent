# Documentation for `stats_svc.calculate_z_scores`

### calculate_z_scores() -> List[float]

**Description:**
Calculates the z-scores for a given dataset. A z-score indicates how many standard deviations an element is from the mean of the dataset, providing a way to understand the relative position of a data point within a distribution.

**Parameters:**
- `data` (`List[float]`): A list of numerical values for which the z-scores will be calculated.

**Expected Input:**
- `data` should be a non-empty list of floats or integers. The values can be positive, negative, or zero, but the list must contain at least one element to compute the mean and standard deviation.

**Returns:**
`List[float]`: A list of z-scores corresponding to the input data, where each z-score represents the number of standard deviations a data point is from the mean.

**Detailed Logic:**
- The function begins by calculating the mean of the input dataset. This is done by summing all the values and dividing by the number of values.
- Next, it computes the standard deviation of the dataset. This involves calculating the variance, which is the average of the squared differences from the mean, and then taking the square root of the variance.
- For each value in the dataset, the function calculates the z-score using the formula: \( z = \frac{(X - \text{mean})}{\text{std\_dev}} \), where \( X \) is the individual data point.
- The resulting z-scores are collected into a list and returned.
- This function does not rely on any external dependencies and operates solely on the provided input data.

---
*Generated with 100% context confidence*
