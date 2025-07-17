# Documentation for `service.perform_independent_ttest`

### service.perform_independent_ttest(data1: list, data2: list, equal_var: bool = True) -> dict

**Description:**
The `perform_independent_ttest` function conducts an independent two-sample t-test to determine if there is a statistically significant difference between the means of two independent datasets. This function is commonly used in statistical analysis to compare the means of two groups when the data is assumed to be normally distributed.

**Parameters:**
- `data1` (`list`): The first dataset, which should be a list of numerical values representing the first group.
- `data2` (`list`): The second dataset, which should also be a list of numerical values representing the second group.
- `equal_var` (`bool`, optional): A flag indicating whether to assume equal variances for the two groups. Defaults to `True`.

**Expected Input:**
- `data1` and `data2` should be lists containing numerical values (integers or floats). Both lists should not be empty.
- The `equal_var` parameter should be a boolean value, where `True` indicates that the variances of the two datasets are assumed to be equal, and `False` indicates that they are not.

**Returns:**
`dict`: A dictionary containing the results of the t-test, including:
- `t_statistic`: The calculated t-statistic value.
- `p_value`: The p-value associated with the t-test, indicating the probability of observing the data if the null hypothesis is true.
- `degrees_of_freedom`: The degrees of freedom used in the test.

**Detailed Logic:**
- The function begins by validating the input datasets to ensure they are non-empty and contain numerical values.
- It then computes the means and variances of both datasets.
- Depending on the `equal_var` flag, it calculates the t-statistic using the appropriate formula for either equal or unequal variances.
- The p-value is computed based on the t-statistic and the degrees of freedom, which is determined by the sizes of the input datasets.
- Finally, the function returns a dictionary containing the t-statistic, p-value, and degrees of freedom, allowing users to interpret the results of the t-test. 

This function does not rely on any external dependencies, making it self-contained for performing independent t-tests.

---
*Generated with 100% context confidence*
