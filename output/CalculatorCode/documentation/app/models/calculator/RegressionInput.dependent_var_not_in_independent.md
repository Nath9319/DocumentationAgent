# Documentation for RegressionInput.dependent_var_not_in_independent

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### RegressionInput.dependent_var_not_in_independent() -> None

**Description:**
This method validates that the dependent variable specified in a regression analysis is not included among the independent variables. It ensures that the model is correctly specified, as including the dependent variable in the independent variables would lead to incorrect model fitting and interpretation.

**Parameters:**
None

**Expected Input:**
- The method operates on the attributes of the `RegressionInput` class, which must have a defined dependent variable and a list of independent variables. The dependent variable should be a string or identifier that represents the outcome being predicted, while the independent variables should be a collection (like a list or set) of strings or identifiers representing the predictors.

**Returns:**
None

**Detailed Logic:**
- The method utilizes the `field_validator` from an external library to perform its validation checks.
- It checks if the dependent variable is present in the collection of independent variables.
- If the dependent variable is found within the independent variables, a `ValueError` is raised, indicating that the dependent variable should not be included in the independent variables.
- This validation is crucial for maintaining the integrity of the regression model and preventing logical errors during analysis.

---
*Generated with 0% context confidence*
