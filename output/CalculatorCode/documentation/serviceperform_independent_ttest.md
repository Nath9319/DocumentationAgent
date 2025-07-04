# Documentation for `service.perform_independent_ttest`

### service.perform_independent_ttest(data1: list, data2: list, equal_var: bool = True) -> dict

**Description:**
The `perform_independent_ttest` function conducts an independent two-sample t-test to determine if there is a statistically significant difference between the means of two independent groups. This function is commonly used in statistical analysis to compare the means of two datasets.

**Parameters:**
- `data1` (`list`): The first dataset, which is a collection of numerical values representing one group.
- `data2` (`list`): The second dataset, which is also a collection of numerical values representing another group.
- `equal_var` (`bool`, optional): A flag indicating whether to assume equal variances for the two groups. Defaults to `True`.

**Expected Input:**
- `data1` and `data2` should be lists containing numerical values (integers or floats). Both lists must not be empty.
- If `equal_var` is set to `True`, it assumes that both groups have the same variance; if `False`, it uses Welch's t-test, which does not assume equal variance.

**Returns:**
`dict`: A dictionary containing the results of the t-test, which typically includes:
- `t_statistic`: The calculated t-statistic value.
- `p_value`: The p-value associated with the t-test, indicating the probability of observing the data if the null hypothesis is true.
- `degrees_of_freedom`: The degrees of freedom used in the test.

**Detailed Logic:**
- The function begins by validating the input datasets to ensure they are non-empty and contain numerical values.
- It then calculates the means and variances of both datasets.
- Depending on the `equal_var` parameter, it either performs a standard independent t-test (assuming equal variances) or Welch's t-test (assuming unequal variances).
- The t-statistic and p-value are computed using the appropriate statistical formulas.
- Finally, the function returns a dictionary containing the t-statistic, p-value, and degrees of freedom, allowing users to interpret the results of the t-test. 

This function does not have any internal dependencies and relies solely on the statistical methods implemented within its logic.

---
*Generated with 100% context confidence*
