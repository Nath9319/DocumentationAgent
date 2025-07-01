# Documentation for `calculate_std_deviation`

```markdown
### calculate_std_deviation(data: list) -> float

**Description:**  
Calculates the standard deviation of a given dataset, which is a measure of the amount of variation or dispersion in a set of values. The function computes the standard deviation by first determining the mean of the dataset, then calculating the variance, and finally taking the square root of the variance to obtain the standard deviation.

**Parameters:**
- `data` (`list`): A list of numerical values for which the standard deviation is to be calculated.

**Expected Input:**  
- `data` should be a non-empty list containing numerical values (integers or floats). The function does not handle empty lists and will raise an exception if provided with one.

**Returns:**  
`float`: The standard deviation of the input dataset, representing the dispersion of the values around the mean.

**Detailed Logic:**  
- The function begins by checking if the input list `data` is empty. If it is, an `APIException` is raised with an appropriate error message and status code.
- It then calculates the mean of the dataset by summing all the values and dividing by the number of values.
- Next, the function computes the variance by iterating over the dataset, calculating the squared difference of each value from the mean, and averaging these squared differences.
- Finally, the standard deviation is obtained by taking the square root of the variance.
- The function relies on basic arithmetic operations and the `math.sqrt` function for the square root calculation, ensuring that the output is a floating-point number representing the standard deviation.
```