# Documentation for `RegressionInput.dependent_var_not_in_independent`

### RegressionInput.dependent_var_not_in_independent() -> None

**Description:**
This method is responsible for validating that the dependent variable specified in a regression analysis is not included in the set of independent variables. It ensures that the model is correctly specified, which is crucial for accurate statistical analysis and predictions.

**Parameters:**
- None

**Expected Input:**
- The method operates on the attributes of the `RegressionInput` class, which should include a list or collection of independent variables and a single dependent variable. The dependent variable must be explicitly defined and should not be present in the list of independent variables.

**Returns:**
`None`: The method does not return a value. Instead, it raises a `ValueError` if the dependent variable is found within the independent variables, indicating a misconfiguration in the regression setup.

**Detailed Logic:**
- The method first retrieves the dependent variable and the list of independent variables from the class attributes.
- It then checks if the dependent variable is present in the list of independent variables.
- If the dependent variable is found within the independent variables, a `ValueError` is raised, providing feedback to the user about the incorrect model specification.
- This validation step is crucial for ensuring that the regression model is correctly set up, as including the dependent variable in the independent variables would invalidate the regression analysis. The method relies on the `field_validator` function to enforce this validation, ensuring that the input adheres to the expected criteria for regression analysis.

---
*Generated with 100% context confidence*
