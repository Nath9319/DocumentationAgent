# Documentation for `StatsService.perform_ols_regression`

```markdown
### StatsService.perform_ols_regression(dependent_var: np.ndarray, independent_vars: np.ndarray) -> dict

**Description:**  
Performs Ordinary Least Squares (OLS) regression using NumPy's least squares method to analyze the relationship between a dependent variable and one or more independent variables. The method computes the regression coefficients, intercept, R-squared value, and p-values, returning a summary dictionary containing these statistics.

**Parameters:**
- `dependent_var` (`np.ndarray`): A one-dimensional NumPy array representing the dependent variable (the outcome variable) in the regression analysis.
- `independent_vars` (`np.ndarray`): A two-dimensional NumPy array where each column represents an independent variable (predictor variable) in the regression model.

**Expected Input:**  
- `dependent_var` must be a one-dimensional array with a length that matches the number of rows in `independent_vars`.
- `independent_vars` should be a two-dimensional array with shape (n_samples, n_features), where `n_samples` is the number of observations and `n_features` is the number of independent variables. The data should be numerical and can include multiple predictors.

**Returns:**  
`dict`: A dictionary containing the following keys and their corresponding values:
- `coefficients`: A NumPy array of the estimated coefficients for each independent variable.
- `intercept`: A float representing the estimated intercept of the regression line.
- `r_squared`: A float indicating the proportion of variance in the dependent variable that can be explained by the independent variables.
- `p_values`: A NumPy array of p-values corresponding to each coefficient, indicating the statistical significance of the predictors.

**Detailed Logic:**  
- The method begins by augmenting the `independent_vars` array with a column of ones to account for the intercept in the regression model.
- It then utilizes NumPy's least squares function to compute the coefficients that minimize the sum of the squared residuals between the observed and predicted values.
- The intercept is extracted from the coefficients, and the predicted values are calculated using the independent variables and the estimated coefficients.
- The method computes the residuals (the differences between the observed and predicted values) and uses these to calculate the R-squared value, which quantifies the goodness of fit of the model.
- Finally, it calculates the p-values for each coefficient to assess their statistical significance, returning all results in a structured dictionary format.
```