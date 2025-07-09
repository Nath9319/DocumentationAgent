# Documentation for `service.perform_independent_ttest`

### service.perform_independent_ttest(data1: list, data2: list, equal_var: bool = True) -> dict

**Description:**
The `perform_independent_ttest` function conducts an independent two-sample t-test to determine if there is a statistically significant difference between the means of two independent groups. This function is commonly used in statistical analysis to compare the means of two datasets.

**Parameters:**
- `data1` (`list`): The first dataset, which is a collection of numerical values representing one group.
- `data2` (`list`): The second dataset, which is a collection of numerical values representing another group.
- `equal_var` (`bool`, optional): A flag indicating whether to assume equal population variances. Defaults to `True`. If set to `False`, the function will use Welch's t-test, which does not assume equal variances.

**Expected Input:**
- `data1` and `data2` should be lists containing numerical values (integers or floats). Both lists must not be empty.
- The `equal_var` parameter should be a boolean value, where `True` indicates that the variances of the two groups are assumed to be equal.

**Returns:**
`dict`: A dictionary containing the results of the t-test, which typically includes:
- `t_statistic`: The calculated t-statistic value.
- `p_value`: The p-value associated with the t-test, indicating the probability of observing the data if the null hypothesis is true.
- `degrees_of_freedom`: The degrees of freedom used in the test.

**Detailed Logic:**
- The function begins by validating the input datasets to ensure they are non-empty and contain numerical values.
- It then calculates the means and standard deviations of both datasets.
- Depending on the `equal_var` flag, the function either:
  - Computes the t-statistic and p-value using the standard independent t-test formula (assuming equal variances).
  - Or, applies Welch's t-test formula (if `equal_var` is `False`), which adjusts for unequal variances.
- Finally, the function returns a dictionary containing the t-statistic, p-value, and degrees of freedom, providing a comprehensive summary of the test results. 

This function does not have any internal dependencies and operates solely on the provided input data.

---
*Generated with 100% context confidence*
