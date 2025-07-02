### MatrixInput

**Description:**  
Model for matrix operations that includes validators and a helper function to facilitate matrix-related computations.

**Parameters / Attributes:**  
| Name          | Type           | Description                                   |
|---------------|----------------|-----------------------------------------------|
| matrix        | list of lists  | A two-dimensional list representing the matrix. |
| rows          | int            | Number of rows in the matrix.                |
| columns       | int            | Number of columns in the matrix.             |

**Expected Input:**  
• `matrix` must be a list of lists, where each inner list has the same length (i.e., all rows must have the same number of columns).  
• `rows` must be a positive integer.  
• `columns` must be a positive integer.

**Returns:**  
`None` – The class does not return a value but initializes a matrix object.

**Detailed Logic:**  
• The class constructor validates the input matrix to ensure it is well-formed (i.e., all rows have the same length).  
• It calculates the number of rows and columns based on the input matrix.  
• Additional helper functions may be provided to perform operations such as addition, multiplication, or transposition of matrices.

**Raises / Errors:**  
• Raises a `ValueError` if the input matrix is not rectangular (i.e., rows of different lengths).  
• Raises a `TypeError` if the input is not a list of lists.

**Usage Example:**  
```python
matrix = MatrixInput([[1, 2], [3, 4]])
```