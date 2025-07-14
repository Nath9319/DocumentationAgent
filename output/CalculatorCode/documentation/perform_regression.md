# Documentation for `perform_regression`

### perform_regression(dependent_var: str, independent_vars: list[str], data: DataFrame) -> RegressionResults

**Description:**
The `perform_regression` function is designed to execute Ordinary Least Squares (OLS) regression analysis on a specified dataset. It estimates the relationships between a dependent variable and one or more independent variables, providing insights into how well the independent variables predict the dependent variable. The function computes regression coefficients and other statistical metrics to evaluate the model's performance.

**Parameters:**
- `dependent_var` (`str`): The name of the dependent variable (outcome variable) in the dataset.
- `independent_vars` (`list[str]`): A list of names of the independent variables (predictor variables) to be included in the regression model.
- `data` (`DataFrame`): A pandas DataFrame containing the dataset on which the regression analysis will be performed. This DataFrame must include columns corresponding to both the dependent and independent variables.

**Expected Input:**
- `dependent_var` must be a string that matches a column name in the provided DataFrame.
- `independent_vars` should be a list of strings, each representing a valid column name in the DataFrame.
- `data` must be a pandas DataFrame with appropriate data types for regression analysis (e.g., numeric types for independent variables).

**Returns:**
`RegressionResults`: An object containing the results of the OLS regression analysis, including coefficients, statistical significance, and goodness-of-fit metrics.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure that the dependent variable and independent variables are present in the provided DataFrame.
- It constructs the regression model using the specified dependent and independent variables.
- The OLS regression is performed using the `stats_svc.perform_ols_regression` function, which computes the regression coefficients and other relevant statistics.
- Finally, the function returns an object encapsulating the results of the regression analysis, allowing users to interpret the findings and assess the model's performance. 

This function is designed to be invoked as part of a web API endpoint, utilizing the `router.post` method to handle incoming POST requests, and may leverage dependency injection via `Depends` for resolving necessary services or configurations. It also incorporates error handling through the `APIException` class to manage any exceptions that arise during the regression analysis process.

---
*Generated with 100% context confidence*
