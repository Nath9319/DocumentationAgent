# Documentation for `RegressionInput.dependent_var_not_in_independent`

### RegressionInput.dependent_var_not_in_independent() -> None

**Description:**
The `dependent_var_not_in_independent` method is responsible for validating that the dependent variable specified in a regression analysis is not included among the independent variables. This is crucial for ensuring the integrity of the regression model, as including the dependent variable in the independent set would lead to incorrect results.

**Parameters:**
None

**Expected Input:**
- The method operates on the attributes of the `RegressionInput` class, which should include a list of independent variables and a single dependent variable. The independent variables must be defined prior to invoking this method.

**Returns:**
None: The method does not return a value. Instead, it raises a `ValueError` if the dependent variable is found within the list of independent variables.

**Detailed Logic:**
- The method begins by checking if the dependent variable is present in the list of independent variables.
- If the dependent variable is found in the independent variables, a `ValueError` is raised to indicate that the dependent variable cannot be included in the independent set.
- This validation is essential to maintain the correctness of the regression analysis and prevent logical errors in model fitting. The method utilizes the `field_validator` function to perform this check, ensuring that the validation process adheres to the defined criteria for input integrity.

---
*Generated with 100% context confidence*
