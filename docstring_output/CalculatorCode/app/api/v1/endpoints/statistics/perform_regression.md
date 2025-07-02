### perform_regression(data: pd.DataFrame, target: str, features: List[str]) -> RegressionResults

**Description:**  
Performs regression analysis on the provided dataset to identify relationships between the target variable and specified features.

**Parameters:**  
| Name     | Type          | Description                                           |
|----------|---------------|-------------------------------------------------------|
| data     | pd.DataFrame  | The input dataset containing the target and features. |
| target   | str           | The name of the target variable to predict.           |
| features | List[str]    | A list of feature names used for prediction.         |

**Expected Input:**  
• `data` must be a pandas DataFrame with the target and feature columns present.  
• `target` should be a valid column name in `data`.  
• `features` must contain valid column names in `data` and should not be empty.  

**Returns:**  
`RegressionResults` – an object containing the results of the regression analysis, including coefficients, intercept, and statistical metrics.

**Detailed Logic:**  
• Validates the input DataFrame to ensure it contains the specified target and feature columns.  
• Splits the data into independent variables (features) and the dependent variable (target).  
• Applies a regression algorithm (e.g., linear regression) to fit the model to the data.  
• Computes and stores the regression coefficients, intercept, and relevant statistical metrics (e.g., R-squared, p-values).  
• Returns the results encapsulated in a `RegressionResults` object for further analysis.

**Raises / Errors:**  
• Raises a `ValueError` if the target or features are not found in the DataFrame.  
• Raises a `TypeError` if the input types are incorrect (e.g., if `data` is not a DataFrame).

**Usage Example:**  
```python
import pandas as pd
from your_module import perform_regression

# Sample data
data = pd.DataFrame({
    'feature1': [1, 2, 3],
    'feature2': [4, 5, 6],
    'target': [7, 8, 9]
})

# Perform regression
results = perform_regression(data, target='target', features=['feature1', 'feature2'])
print(results)
```