# Documentation for `StatsService.perform_independent_ttest`

### StatsService.perform_independent_ttest(sample1: Union[List[float], np.ndarray], sample2: Union[List[float], np.ndarray], equal_var: bool = True, alternative: str = 'two-sided') -> Ttest_indResult

**Description:**
The `perform_independent_ttest` method conducts an independent two-sample t-test to evaluate whether the means of two independent samples are statistically significantly different. This method leverages the `stats.ttest_ind` function from the SciPy library to perform the test, providing users with a robust statistical analysis tool for hypothesis testing.

**Parameters:**
- `sample1` (`Union[List[float], np.ndarray]`): The first sample data, which can be provided as a list or a NumPy array containing numerical values.
- `sample2` (`Union[List[float], np.ndarray]`): The second sample data, structured similarly to `sample1`.
- `equal_var` (`bool`, optional): A flag that indicates whether to assume equal population variances. If set to `True`, the method uses the standard independent t-test; if `False`, it applies Welch's t-test, which is more appropriate when variances are unequal. The default value is `True`.
- `alternative` (`str`, optional): Specifies the alternative hypothesis for the test. It can take one of the following values:
  - `'two-sided'`: Tests if the means are different (default).
  - `'less'`: Tests if the mean of `sample1` is less than the mean of `sample2`.
  - `'greater'`: Tests if the mean of `sample1` is greater than the mean of `sample2`.

**Expected Input:**
- Both `sample1` and `sample2` should be array-like structures (lists or NumPy arrays) containing numerical data. They can vary in length.
- The `equal_var` parameter should be a boolean value, either `True` or `False`.
- The `alternative` parameter should be a string that matches one of the specified options.

**Returns:**
`Ttest_indResult`: An object that encapsulates the results of the t-test, including the t-statistic and the p-value, along with additional information about the test outcome.

**Detailed Logic:**
- The method begins by validating the input samples to ensure they are appropriate for statistical testing.
- It calculates the means and variances of both samples.
- Depending on the value of the `equal_var` parameter, the method either computes the standard t-test (assuming equal variances) or Welch's t-test (which does not assume equal variances).
- The t-statistic is calculated based on the selected test, and the p-value is derived from this statistic in relation to the specified alternative hypothesis.
- Finally, the method returns a `Ttest_indResult` object that contains the t-statistic and p-value, allowing users to interpret the significance of the results.

---
*Generated with 100% context confidence*
