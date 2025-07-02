### CorrelationInput

**Description:**  
Model for correlation matrix. Ensures at least two columns are provided if specified.

**Parameters / Attributes:**  
| Name       | Type   | Description                                           |
|------------|--------|-------------------------------------------------------|
| columns    | list   | List of columns to be included in the correlation matrix. |

**Expected Input:**  
• `columns` must contain at least two elements.  
• Each element in `columns` should be of a compatible data type for correlation analysis (e.g., numeric types).

**Returns:**  
`CorrelationMatrix` – an object representing the correlation matrix based on the provided columns.

**Detailed Logic:**  
• The model checks the length of the `columns` list to ensure it contains at least two elements.  
• If the condition is met, it proceeds to compute the correlation matrix using the specified columns.  
• The correlation matrix is generated based on the statistical relationships between the provided columns.

**Raises / Errors:**  
• Raises a `ValueError` if fewer than two columns are provided.  

**Usage Example:**  
```python
# Example usage of CorrelationInput
correlation_input = CorrelationInput(columns=[data_column1, data_column2])
correlation_matrix = correlation_input.compute()
```