# Documentation for `StatsService.perform_independent_ttest`

### StatsService.perform_independent_ttest(sample1: Union[List[float], np.ndarray], sample2: Union[List[float], np.ndarray]) -> Tuple[float, float]

**Description:**  
Performs an independent two-sample t-test to determine if there is a statistically significant difference between the means of two independent samples. This method is commonly used in hypothesis testing to compare the means of two groups.

**Parameters:**
- `sample1` (`Union[List[float], np.ndarray]`): The first sample of data, which can be provided as a list of floats or a NumPy array.
- `sample2` (`Union[List[float], np.ndarray]`): The second sample of data, which can also be provided as a list of floats or a NumPy array.

**Expected Input:**  
- Both `sample1` and `sample2` should contain numerical data (floats) and can be either a list or a NumPy array.
- Each sample should ideally contain more than one data point to ensure the validity of the t-test.
- The samples should be independent of each other, meaning the data points in one sample do not influence the data points in the other.

**Returns:**  
`Tuple[float, float]`: A tuple containing two values:
1. The t-statistic (`float`): A value that indicates the size of the difference relative to the variation in the sample data.
2. The p-value (`float`): The probability that the observed data would occur if the null hypothesis were true, which helps in determining statistical significance.

**Detailed Logic:**  
- The method begins by validating the input samples to ensure they are of the correct type and contain sufficient data points.
- It calculates the means and standard deviations of both samples.
- The t-statistic is computed using the formula that accounts for the means, standard deviations, and sizes of both samples.
- The method then calculates the degrees of freedom for the t-test, which is essential for determining the critical value from the t-distribution.
- Finally, it computes the p-value associated with the t-statistic, which indicates the likelihood of observing the data under the null hypothesis.
- This method does not rely on any external libraries beyond those typically used for statistical calculations, ensuring that it operates independently within the `StatsService` class.