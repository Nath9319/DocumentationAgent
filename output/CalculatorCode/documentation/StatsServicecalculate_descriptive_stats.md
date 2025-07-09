# Documentation for `StatsService.calculate_descriptive_stats`

### StatsService.calculate_descriptive_stats(data: list) -> dict

**Description:**
Calculates descriptive statistics for a given list of numerical values. This method computes the mean, median, mode, variance, and standard deviation of the input data and returns these statistics in a dictionary format. It is useful for summarizing the central tendency and dispersion of the dataset.

**Parameters:**
- `data` (`list`): A list of numerical values (integers or floats) for which the descriptive statistics will be calculated.

**Expected Input:**
- `data` should be a non-empty list containing numerical values. The list can include both integers and floats. If the list is empty, the function may raise an error or return a specific value indicating that no statistics can be computed.

**Returns:**
`dict`: A dictionary containing the following descriptive statistics:
- `mean` (`float`): The average of the input values.
- `median` (`float`): The middle value of the input data when sorted.
- `mode` (`Union[int, float]`: The most frequently occurring value in the dataset.
- `variance` (`float`): A measure of how much the values deviate from the mean.
- `standard_deviation` (`float`): The square root of the variance, representing the dispersion of the dataset.

**Detailed Logic:**
- The function begins by validating the input to ensure it is a non-empty list of numerical values.
- It calculates the mean using the `np.mean` function, which sums the elements and divides by the count.
- The median is computed using the `np.median` function, which sorts the values and finds the middle element.
- The mode is determined using the `stats.mode` function, which identifies the most frequently occurring value in the dataset.
- Variance is calculated using the `np.var` function, which measures the average of the squared differences from the mean.
- Finally, the standard deviation is computed using the `np.std` function, which provides a measure of the amount of variation or dispersion in the dataset.
- The results are compiled into a dictionary and returned, providing a comprehensive summary of the descriptive statistics for the input data.

---
*Generated with 100% context confidence*
