# Documentation for `RegressionInput`

```python
class RegressionInput:
    """
    Model for Ordinary Least Squares (OLS) regression.

    This class is designed to ensure that the dependent variable is distinct from the independent variables 
    used in the regression analysis. It incorporates validation to prevent the inclusion of the dependent 
    variable in the list of independent variables, which would invalidate the regression model.

    Attributes:
        dependent_var (str): The variable that is being predicted.
        independent_vars (list): A list of variables used to predict the dependent variable.

    Methods:
        dependent_var_not_in_independent(v, values):
            Validates that the dependent variable is not included in the list of independent variables.
    """

    # Class implementation goes here
```

### Key Points of the Documentation:
- **Purpose:** The docstring provides a clear overview of the class's role in OLS regression and its validation mechanism.
- **Attributes:** It describes the key attributes of the class, specifying their types and purposes.
- **Methods:** It briefly mentions the validation method, linking it to the class's functionality.