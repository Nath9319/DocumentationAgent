### get_correlation_matrix(data: pd.DataFrame) -> pd.DataFrame

**Description:**  
Calculates the correlation matrix for the given dataset, providing insights into the relationships between different variables.

**Parameters:**  
| Name   | Type        | Description                                   |
|--------|-------------|-----------------------------------------------|
| data   | pd.DataFrame | A pandas DataFrame containing numerical data for which the correlation matrix is to be computed. |

**Expected Input:**  
• `data` should be a pandas DataFrame with at least two numerical columns.  
• The DataFrame may contain NaN values, which should be handled appropriately (e.g., ignored or filled).  
• All columns in the DataFrame should be of numeric types (int, float).

**Returns:**  
`pd.DataFrame` – A DataFrame representing the correlation matrix, where each cell (i, j) contains the correlation coefficient between the i-th and j-th variables.

**Detailed Logic:**  
• The function first checks the input DataFrame for validity, ensuring it contains the required numerical data.  
• It then computes the correlation coefficients using a statistical method (e.g., Pearson correlation) across all pairs of variables in the DataFrame.  
• The resulting correlation coefficients are organized into a new DataFrame, which is returned to the caller.

**Raises / Errors:**  
• Raises a `ValueError` if the input DataFrame does not contain enough numerical data to compute a correlation matrix.  
• Raises a `TypeError` if the input is not a pandas DataFrame.

**Usage Example:**  
```python
import pandas as pd

# Sample data
data = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [4, 3, 2, 1],
    'C': [1, 3, 2, 4]
})

# Calculate correlation matrix
correlation_matrix = get_correlation_matrix(data)
print(correlation_matrix)
```