# Documentation for `perform_ttest`

```markdown
### perform_ttest(data1: list, data2: list) -> float

**Description:**  
The `perform_ttest` function conducts a two-sample t-test to determine if there is a statistically significant difference between the means of two independent samples. It evaluates the null hypothesis that the two samples have identical average values.

**Parameters:**
- `data1` (`list`): The first sample of numerical data.
- `data2` (`list`): The second sample of numerical data.

**Expected Input:**  
- Both `data1` and `data2` should be lists containing numerical values (integers or floats). 
- The lists should not be empty, as a t-test requires at least one data point in each sample.
- The data should ideally be normally distributed, and the variances of the two samples should be similar for the t-test assumptions to hold.

**Returns:**  
`float`: The p-value resulting from the t-test, which indicates the probability of observing the data assuming the null hypothesis is true. A lower p-value suggests stronger evidence against the null hypothesis.

**Detailed Logic:**  
- The function begins by validating the input data to ensure that both samples are non-empty and contain valid numerical values.
- It then calculates the means and standard deviations of both samples.
- Using these statistics, the function computes the t-statistic and the degrees of freedom for the t-test.
- Finally, it calculates the p-value based on the t-statistic and the degrees of freedom, which is returned as the output.
- If any errors occur during the computation (e.g., invalid data types or empty lists), the function raises an `APIException` with an appropriate error message and status code, ensuring that error handling is consistent with the API's structure.
```