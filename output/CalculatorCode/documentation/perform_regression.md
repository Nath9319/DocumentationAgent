# Documentation for `perform_regression`

```markdown
### perform_regression(data: List[Dict[str, Any]], target: str) -> Dict[str, Any]

**Description:**  
The `perform_regression` function is designed to execute a regression analysis on a given dataset. It processes the input data to identify relationships between the specified target variable and other features, ultimately returning the results of the regression analysis in a structured format.

**Parameters:**
- `data` (`List[Dict[str, Any]]`): A list of dictionaries where each dictionary represents a data point with various features and their corresponding values.
- `target` (`str`): The name of the target variable (the dependent variable) that the regression analysis aims to predict.

**Expected Input:**  
- `data` should be a non-empty list containing dictionaries. Each dictionary must have keys corresponding to feature names, including the target variable specified by the `target` parameter.
- `target` should be a string that matches one of the keys in the dictionaries within `data`. If the target variable is not present in the data, the function will raise an exception.

**Returns:**  
`Dict[str, Any]`: A dictionary containing the results of the regression analysis, which may include coefficients, intercepts, statistical significance, and other relevant metrics.

**Detailed Logic:**  
- The function begins by validating the input data to ensure that it is not empty and that the target variable exists within the provided dataset.
- It then preprocesses the data, which may involve handling missing values, encoding categorical variables, and normalizing numerical features.
- Following preprocessing, the function applies a regression algorithm (such as linear regression) to model the relationship between the target variable and the other features.
- The results of the regression analysis are compiled into a dictionary format, which is then returned to the caller.
- If any errors occur during processing (e.g., invalid input data or issues with the regression computation), the function raises an `APIException` with an appropriate error message and status code, ensuring consistent error handling throughout the API.
```