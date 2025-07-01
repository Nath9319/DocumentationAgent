# Documentation for `perform_ttest`

### perform_ttest(data: List[float], alpha: float = 0.05) -> Dict[str, Any]

**Description:**
The `perform_ttest` function conducts an independent two-sample t-test on the provided dataset. It evaluates whether the means of two independent groups are statistically different from each other. This function is typically used in statistical analysis to determine if there is enough evidence to reject the null hypothesis, which states that there is no difference between the group means.

**Parameters:**
- `data` (`List[float]`): A list of numerical values representing the two independent samples to be compared.
- `alpha` (`float`, optional): The significance level for the t-test, defaulting to 0.05. This value determines the threshold for rejecting the null hypothesis.

**Expected Input:**
- `data` should be a list containing two sets of numerical values (e.g., [group1_values, group2_values]). Each group should have at least two observations for the t-test to be valid.
- `alpha` should be a float between 0 and 1, representing the probability of rejecting the null hypothesis when it is true.

**Returns:**
`Dict[str, Any]`: A dictionary containing the results of the t-test, including:
- `t_statistic`: The calculated t-statistic value.
- `p_value`: The p-value associated with the t-test.
- `reject_null`: A boolean indicating whether to reject the null hypothesis based on the p-value and the significance level.

**Detailed Logic:**
- The function begins by validating the input data to ensure it contains two independent samples.
- It then calls the `service.perform_independent_ttest` function, passing the validated data and the significance level.
- The results from the t-test are processed, and the t-statistic and p-value are extracted.
- Finally, the function evaluates whether the p-value is less than the specified alpha level to determine if the null hypothesis should be rejected, and it constructs a result dictionary to return these findings.
- The function is designed to handle exceptions gracefully, potentially raising an `APIException` if any errors occur during the execution of the t-test, ensuring robust error handling within the API framework.