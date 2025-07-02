### RegressionInput

**Description:**  
Model for Ordinary Least Squares (OLS) regression. This class ensures that the variables used in the regression model are distinct, preventing multicollinearity issues.

**Parameters / Attributes:**  
| Name          | Type   | Description                                         |
|---------------|--------|-----------------------------------------------------|
| variables     | list   | List of variables to be used in the regression model. |
| target        | str    | The target variable that the model aims to predict.  |

**Expected Input:**  
• `variables` must be a list of distinct variable names (strings).  
• `target` must be a string representing the name of the target variable.  
• The length of `variables` must be greater than zero and should not include duplicates.

**Returns:**  
`None` – This class does not return a value upon instantiation but sets up the model for further operations.

**Detailed Logic:**  
• The constructor initializes the `variables` and `target` attributes.  
• It checks for duplicates in the `variables` list to ensure all variables are distinct.  
• If duplicates are found, an error is raised, preventing the creation of a model with multicollinearity issues.

**Raises / Errors:**  
• Raises a `ValueError` if the `variables` list contains duplicates.

**Usage Example:**  
```python
# Creating an instance of RegressionInput
regression_input = RegressionInput(variables=['age', 'income', 'education'], target='salary')
```