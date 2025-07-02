# Documentation for `RegressionInput.dependent_var_not_in_independent`

### RegressionInput.dependent_var_not_in_independent() -> None

**Description:**
The `dependent_var_not_in_independent` method is designed to validate that the dependent variable specified for a regression analysis is not included in the set of independent variables. This is a crucial step in ensuring the integrity of regression models, as including the dependent variable among the independent variables can lead to misleading results.

**Parameters:**
None

**Expected Input:**
- The method operates on the attributes of the `RegressionInput` class, which should include:
  - `dependent_var`: A string representing the name of the dependent variable.
  - `independent_vars`: A list of strings representing the names of the independent variables.
- It is expected that `dependent_var` and `independent_vars` are properly initialized before calling this method.

**Returns:**
None

**Detailed Logic:**
- The method first checks if the `dependent_var` is present in the `independent_vars` list.
- If the dependent variable is found within the independent variables, the method raises a `ValueError`, indicating that the dependent variable cannot be included in the independent variables.
- This validation helps maintain the integrity of the regression model by ensuring that the dependent variable is distinct from the independent variables, thereby preventing potential issues in the analysis. 
- The method utilizes the `field_validator` function to perform the validation check, ensuring that the input adheres to the expected criteria for regression analysis.

---
*Generated with 100% context confidence*
