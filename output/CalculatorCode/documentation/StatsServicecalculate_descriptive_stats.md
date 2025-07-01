# Documentation for `StatsService.calculate_descriptive_stats`

### calculate_descriptive_stats(numbers: List[float]) -> Dict[str, float]

**Description:**
Calculates descriptive statistics for a given list of numerical values. This method computes key statistical measures including the mean, median, mode, variance, and standard deviation, providing a comprehensive overview of the data's distribution.

**Parameters:**
- `numbers` (`List[float]`): A list of numerical values for which the descriptive statistics will be calculated.

**Expected Input:**
- `numbers` should be a non-empty list of floats or integers. The list can contain any real numbers, but it should not be empty, as this would lead to undefined statistical measures.

**Returns:**
`Dict[str, float]`: A dictionary containing the following descriptive statistics:
- `mean`: The average of the numbers.
- `median`: The middle value when the numbers are sorted.
- `mode`: The most frequently occurring value in the list.
- `variance`: A measure of how much the numbers vary from the mean.
- `standard_deviation`: The square root of the variance, indicating the average distance of each number from the mean.

**Detailed Logic:**
- The method begins by validating the input to ensure that the list is not empty.
- It then utilizes the `np.mean` function from the NumPy library to calculate the mean of the numbers.
- The median is computed using `np.median`, which sorts the list and finds the middle value.
- The mode is determined using `stats.mode` from the SciPy library, which identifies the most common value in the list.
- Variance is calculated using `np.var`, which measures the average of the squared differences from the mean.
- Finally, the standard deviation is obtained using `np.std`, providing insight into the dispersion of the dataset.
- The results are compiled into a dictionary and returned, allowing easy access to each statistical measure.