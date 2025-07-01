# Documentation for `perform_regression`

### perform_regression(data: dict, model_type: str) -> dict

**Description:**
The `perform_regression` function executes a regression analysis on the provided dataset using a specified regression model type. It validates the input data, performs the regression analysis, and returns the results in a structured format. This function is designed to facilitate statistical analysis within the application, allowing users to derive insights from their data.

**Parameters:**
- `data` (`dict`): A dictionary containing the dataset to be analyzed. The expected structure of this dictionary should conform to the requirements of the regression analysis.
- `model_type` (`str`): A string indicating the type of regression model to be used (e.g., "OLS" for Ordinary Least Squares). This parameter determines the algorithm that will be applied to the data.

**Expected Input:**
- `data` should be a dictionary with keys representing variable names and values as lists of numerical data points. The data should not contain any missing values or non-numeric entries.
- `model_type` must be a valid string that corresponds to one of the supported regression models. If an unsupported model type is provided, the function should raise an appropriate exception.

**Returns:**
`dict`: A dictionary containing the results of the regression analysis, which may include coefficients, statistical metrics (e.g., R-squared, p-values), and any other relevant output based on the regression model used.

**Detailed Logic:**
- The function begins by validating the input parameters using the `validator.validate_regression_inputs` function, which ensures that the data structure and model type are appropriate for regression analysis.
- Upon successful validation, the function calls `stats_svc.perform_ols_regression` (or another relevant regression function based on the `model_type`) to execute the regression analysis on the provided dataset.
- The results from the regression analysis are then formatted into a dictionary, which is returned to the caller.
- If any errors occur during validation or regression execution, the function raises an `APIException`, allowing for structured error handling and reporting within the API framework.