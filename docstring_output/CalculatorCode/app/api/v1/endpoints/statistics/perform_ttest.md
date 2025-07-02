### perform_ttest(data1: list, data2: list, alternative: str = 'two-sided') -> dict

**Description:**  
Conducts a t-test to determine if there is a statistically significant difference between the means of two independent samples.

**Parameters:**  
| Name       | Type   | Description                                           |
|------------|--------|-------------------------------------------------------|
| data1      | list   | First sample of data points                           |
| data2      | list   | Second sample of data points                          |
| alternative | str    | Defines the alternative hypothesis ('two-sided', 'less', 'greater') |

**Expected Input:**  
• `data1` and `data2` must be lists of numerical values.  
• Both lists should contain at least two data points.  
• The `alternative` parameter must be one of the following strings: 'two-sided', 'less', or 'greater'.

**Returns:**  
`dict` – A dictionary containing the t-statistic, p-value, and degrees of freedom for the test.

**Detailed Logic:**  
• Validates input data to ensure both samples are lists of numerical values.  
• Checks that each sample has at least two data points.  
• Computes the t-statistic and p-value using the appropriate statistical formulas based on the chosen alternative hypothesis.  
• Returns a dictionary with the computed values, allowing for easy access to the results.

**Raises / Errors:**  
• Raises `ValueError` if either `data1` or `data2` does not meet the input requirements.  
• Raises `TypeError` if the data points are not numerical.

**Usage Example:**  
```python
result = perform_ttest([1, 2, 3], [4, 5, 6], alternative='two-sided')
print(result)
```