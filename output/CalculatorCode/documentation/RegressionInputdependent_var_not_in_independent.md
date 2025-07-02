# Documentation for `RegressionInput.dependent_var_not_in_independent`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### RegressionInput.dependent_var_not_in_independent() -> None

**Description:**
This method is designed to validate that the dependent variable specified in a regression analysis is not included among the independent variables. It ensures the integrity of the regression model by preventing the dependent variable from being mistakenly treated as an independent variable, which could lead to erroneous results.

**Parameters:**
None

**Expected Input:**
- The method operates within the context of a regression model where the dependent variable and independent variables are defined. It assumes that these variables are accessible as attributes of the `RegressionInput` class instance.

**Returns:**
`None`: This method does not return any value. Instead, it raises a `ValueError` if the validation check fails.

**Detailed Logic:**
- The method utilizes the `field_validator` from an external library to perform its validation checks. 
- It checks if the dependent variable is present in the list of independent variables.
- If the dependent variable is found among the independent variables, a `ValueError` is raised, indicating that the dependent variable should not be included in the independent variables.
- This validation helps maintain the correctness of the regression model setup, ensuring that the analysis is based on a proper distinction between dependent and independent variables.

---
*Generated with 0% context confidence*
