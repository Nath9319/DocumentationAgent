# Documentation for `StatsService.perform_independent_ttest`

### StatsService.perform_independent_ttest(sample1: Union[List[float], np.ndarray], sample2: Union[List[float], np.ndarray]) -> Tuple[float, float]

**Description:**
The `perform_independent_ttest` method conducts an independent two-sample t-test to determine if there is a statistically significant difference between the means of two independent samples. This method is particularly useful in hypothesis testing where the goal is to compare the means of two groups.

**Parameters:**
- `sample1` (`Union[List[float], np.ndarray]`): The first sample of data, which can be provided as a list of floats or a NumPy array.
- `sample2` (`Union[List[float], np.ndarray]`): The second sample of data, which can also be provided as a list of floats or a NumPy array.

**Expected Input:**
- Both `sample1` and `sample2` should contain numerical data (floats) and can be either lists or NumPy arrays. 
- The samples should not be empty; each sample should contain at least one data point to perform the t-test.
- The data in both samples should ideally be normally distributed for the t-test assumptions to hold true.

**Returns:**
`Tuple[float, float]`: A tuple containing two values:
- The first value is the t-statistic, which indicates the size of the difference relative to the variation in the sample data.
- The second value is the p-value, which helps determine the statistical significance of the observed difference.

**Detailed Logic:**
- The method utilizes the `ttest_ind` function from the `scipy.stats` module to perform the t-test.
- It first validates the input samples to ensure they are of the correct type and contain sufficient data points.
- The `ttest_ind` function is called with the two samples as arguments, which computes the t-statistic and p-value.
- The results are returned as a tuple, allowing the caller to interpret the statistical significance of the difference between the two samples.