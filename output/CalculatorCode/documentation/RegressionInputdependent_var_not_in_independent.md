# Documentation for `RegressionInput.dependent_var_not_in_independent`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### RegressionInput.dependent_var_not_in_independent() -> None

**Description:**
This method is designed to validate that the dependent variable specified for a regression analysis is not included among the independent variables. It ensures that the model is correctly specified, as including the dependent variable in the set of independent variables would lead to incorrect model fitting and interpretation.

**Parameters:**
None

**Expected Input:**
- The method operates on the attributes of the `RegressionInput` class, which should contain a list of independent variables and a dependent variable. The dependent variable must be a single entity that is checked against the list of independent variables.

**Returns:**
None

**Detailed Logic:**
- The method utilizes the `field_validator` from an external library to perform its validation checks.
- It checks if the dependent variable is present in the list of independent variables.
- If the dependent variable is found within the independent variables, a `ValueError` is raised, indicating that the dependent variable cannot be included in the independent variable list.
- This validation step is crucial for maintaining the integrity of the regression model and preventing logical errors during analysis.

---
*Generated with 0% context confidence*
