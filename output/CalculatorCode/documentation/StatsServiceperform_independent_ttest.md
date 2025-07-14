# Documentation for `StatsService.perform_independent_ttest`

### StatsService.perform_independent_ttest(sample1: Union[list, np.ndarray], sample2: Union[list, np.ndarray], equal_var: bool = True, alternative: str = 'two-sided') -> Ttest_indResult

**Description:**
The `perform_independent_ttest` method conducts an independent two-sample t-test to evaluate whether the means of two independent samples are statistically different from each other. This method is essential for hypothesis testing in various fields, allowing researchers to compare the means of two groups based on their sample data.

**Parameters:**
- `sample1` (`Union[list, np.ndarray]`): The first sample data, which can be provided as a list or a NumPy array containing numerical values.
- `sample2` (`Union[list, np.ndarray]`): The second sample data, also provided as a list or a NumPy array for comparison.
- `equal_var` (`bool`, optional): A flag indicating whether to assume equal population variances. Defaults to `True`. If set to `False`, Welch’s t-test is performed, which does not assume equal variance.
- `alternative` (`str`, optional): Specifies the alternative hypothesis. Options include:
  - `'two-sided'`: Tests for the possibility of the relationship in both directions (default).
  - `'less'`: Tests if the mean of `sample1` is less than the mean of `sample2`.
  - `'greater'`: Tests if the mean of `sample1` is greater than the mean of `sample2`.

**Expected Input:**
- Both `sample1` and `sample2` should be array-like structures (lists or NumPy arrays) containing numerical data. They can vary in length.
- The `equal_var` parameter should be a boolean value, either `True` or `False`.
- The `alternative` parameter should be a string that matches one of the specified options.

**Returns:**
`Ttest_indResult`: An object that encapsulates the t-statistic and the two-tailed p-value, providing insights into the statistical significance of the observed differences between the two sample means.

**Detailed Logic:**
- The method begins by validating the input samples `sample1` and `sample2` to ensure they are suitable for statistical analysis.
- It then calculates the means and standard deviations of both samples.
- Depending on the value of `equal_var`, the method either computes the t-statistic using pooled variance (if `equal_var` is `True`) or applies Welch’s method (if `equal_var` is `False`).
- The degrees of freedom for the test are calculated based on the sample sizes and variances.
- Finally, the method computes the p-value associated with the t-statistic, indicating the likelihood of observing the data under the null hypothesis.
- The results are returned as a `Ttest_indResult` object, which contains both the t-statistic and p-value for further interpretation.

---
*Generated with 100% context confidence*
