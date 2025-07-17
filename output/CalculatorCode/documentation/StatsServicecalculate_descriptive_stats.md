# Documentation for `StatsService.calculate_descriptive_stats`

### StatsService.calculate_descriptive_stats(numbers: list) -> dict

**Description:**
Calculates descriptive statistics for a given list of numerical values. This method computes key statistical metrics including the mean, median, mode, variance, and standard deviation, returning these values in a structured dictionary format. It serves as a comprehensive tool for analyzing the central tendency and dispersion of the dataset.

**Parameters:**
- `numbers` (`list`): A list of numerical values (integers or floats) for which the descriptive statistics will be calculated.

**Expected Input:**
- `numbers` should be a non-empty list containing numeric data types. The list can include integers and floats. If the list is empty or contains non-numeric types, the function may raise an error or return undefined results.

**Returns:**
`dict`: A dictionary containing the calculated descriptive statistics:
- `mean` (`float`): The average of the numbers.
- `median` (`float`): The middle value when the numbers are sorted.
- `mode` (`Union[int, float]`): The most frequently occurring value in the list.
- `variance` (`float`): A measure of how much the numbers deviate from the mean.
- `standard_deviation` (`float`): The square root of the variance, indicating the dispersion of the dataset.

**Detailed Logic:**
- The method begins by validating the input list `numbers` to ensure it is non-empty and contains valid numerical values.
- It utilizes the NumPy library to compute the mean and median using `np.mean` and `np.median`, respectively. These functions efficiently handle the calculations and return the average and middle values of the dataset.
- The mode is calculated using the `stats.mode` function, which identifies the most frequently occurring value in the list. In cases of multiple modes, it returns the smallest mode.
- Variance and standard deviation are computed using `np.var` and `np.std`, respectively. These functions determine the spread of the dataset by calculating how much the values deviate from the mean.
- Finally, the method organizes all computed statistics into a dictionary and returns it, providing a structured summary of the descriptive statistics for the input list.

---
*Generated with 100% context confidence*
