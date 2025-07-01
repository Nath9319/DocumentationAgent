# Documentation for `get_z_scores`

```markdown
### get_z_scores(data: List[float]) -> List[float]

**Description:**  
Calculates the z-scores for a given list of numerical data. A z-score indicates how many standard deviations an element is from the mean of the dataset, providing a way to understand the relative position of each data point within the distribution.

**Parameters:**
- `data` (`List[float]`): A list of numerical values for which the z-scores will be calculated.

**Expected Input:**  
- `data` should be a non-empty list of floats or integers. The list must contain numerical values only, as non-numeric types will lead to errors during computation.

**Returns:**  
`List[float]`: A list of z-scores corresponding to each value in the input list. Each z-score represents the number of standard deviations a data point is from the mean.

**Detailed Logic:**  
- The function begins by calculating the mean of the input data.
- It then computes the standard deviation of the data points.
- For each value in the input list, the function calculates the z-score using the formula: \( z = \frac{(X - \text{mean})}{\text{std\_dev}} \), where \( X \) is the individual data point.
- The calculated z-scores are collected into a list and returned.
- If the input data is invalid (e.g., empty or contains non-numeric values), the function raises an `APIException` with an appropriate error message and status code, ensuring consistent error handling throughout the API.
```