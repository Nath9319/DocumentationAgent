# Documentation for `StatsService.calculate_descriptive_stats`

### calculate_descriptive_stats(numbers: list) -> dict

**Description:**  
Calculates descriptive statistics for a given list of numbers. This method computes key statistical measures including the mean, median, mode, variance, and standard deviation, and returns these values in a structured dictionary format.

**Parameters:**
- `numbers` (`list`): A list of numerical values (integers or floats) for which the descriptive statistics will be calculated.

**Expected Input:**  
- `numbers` should be a non-empty list containing numeric values. The list can include integers and/or floating-point numbers. If the list is empty, the function may raise an error or return an empty dictionary, depending on the implementation.

**Returns:**  
`dict`: A dictionary containing the calculated descriptive statistics. The keys of the dictionary include:
- `mean`: The average of the numbers.
- `median`: The middle value when the numbers are sorted.
- `mode`: The most frequently occurring number(s) in the list.
- `variance`: A measure of how much the numbers vary from the mean.
- `standard_deviation`: The square root of the variance, representing the dispersion of the numbers.

**Detailed Logic:**  
- The method begins by validating the input to ensure that the list is not empty.
- It then computes the mean by summing all the numbers and dividing by the count of numbers.
- The median is calculated by sorting the list and finding the middle value, taking into account whether the count of numbers is odd or even.
- The mode is determined by identifying the number(s) that appear most frequently in the list.
- Variance is calculated by averaging the squared differences from the mean, providing insight into the spread of the numbers.
- Finally, the standard deviation is derived as the square root of the variance, offering a measure of variability in the same units as the original numbers.
- The results are compiled into a dictionary and returned, allowing for easy access to the computed statistics.