# Documentation for `StatsService.perform_independent_ttest`

### StatsService.perform_independent_ttest(sample1: Union[List[float], np.ndarray], sample2: Union[List[float], np.ndarray], equal_var: bool = True, alternative: str = 'two-sided') -> Ttest_indResult

**Description:**
The `perform_independent_ttest` method conducts an independent two-sample t-test to evaluate whether the means of two independent samples are statistically significantly different. This method is a wrapper around the `stats.ttest_ind` function, which is commonly utilized in hypothesis testing scenarios.

**Parameters:**
- `sample1` (`Union[List[float], np.ndarray]`): The first sample data, which can be provided as a list or a NumPy array containing numerical values.
- `sample2` (`Union[List[float], np.ndarray]`): The second sample data, structured similarly to `sample1`.
- `equal_var` (`bool`, optional): A flag indicating whether to assume equal population variances. Defaults to `True`, which applies the standard t-test. If set to `False`, Welch’s t-test is used, which is more appropriate when the variances of the two samples are unequal.
- `alternative` (`str`, optional): Specifies the alternative hypothesis. Options include:
  - `'two-sided'`: Tests if the means are different (default).
  - `'less'`: Tests if the mean of `sample1` is less than the mean of `sample2`.
  - `'greater'`: Tests if the mean of `sample1` is greater than the mean of `sample2`.

**Expected Input:**
- Both `sample1` and `sample2` should be numerical data arrays (lists or NumPy arrays) containing observations from two independent samples.
- The input data should not contain NaN values, as they may lead to invalid test results.
- The `equal_var` parameter must be a boolean value, and the `alternative` parameter should be one of the specified string options.

**Returns:**
`Ttest_indResult`: An object containing the t-statistic and the p-value for the test, along with additional information about the test results.

**Detailed Logic:**
- The method begins by validating the input data to ensure that both samples are compatible in shape and contain valid numerical values.
- It calculates the means and standard deviations of both samples.
- Depending on the value of the `equal_var` parameter, it computes either the standard t-test (assuming equal variances) or Welch’s t-test (for unequal variances):
  - For the standard t-test, it calculates the pooled standard deviation.
  - For Welch’s t-test, it computes the standard error using the individual sample variances.
- The t-statistic is then calculated based on the difference between the sample means, adjusted for the standard error.
- Finally, the method calculates the p-value using the t-distribution, which indicates the probability of observing the data under the null hypothesis.
- The results, including the t-statistic and p-value, are returned in a structured format for easy interpretation.

---
*Generated with 100% context confidence*
