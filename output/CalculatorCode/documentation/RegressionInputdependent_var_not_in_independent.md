# Documentation for `RegressionInput.dependent_var_not_in_independent`

### RegressionInput.dependent_var_not_in_independent() -> None

**Description:**
This method is designed to validate that the dependent variable specified in a regression analysis is not included among the independent variables. It ensures that the model is correctly specified, which is crucial for accurate statistical analysis and interpretation.

**Parameters:**
None

**Expected Input:**
- The method operates on the attributes of the `RegressionInput` class, which should include a list of independent variables and a dependent variable. The dependent variable must be a single entity that is not part of the independent variable list.

**Returns:**
`None`: This method does not return a value. Instead, it raises an exception if the validation fails.

**Detailed Logic:**
- The method utilizes a field validator to check if the dependent variable is present in the list of independent variables.
- If the dependent variable is found within the independent variables, a `ValueError` is raised, indicating that the dependent variable should not be included in the independent variables.
- This validation is essential to prevent model mis-specification, which can lead to incorrect conclusions from the regression analysis. The method ensures that the integrity of the regression model is maintained by enforcing this rule.