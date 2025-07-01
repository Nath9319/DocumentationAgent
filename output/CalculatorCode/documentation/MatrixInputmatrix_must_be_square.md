# Documentation for `MatrixInput.matrix_must_be_square`

### MatrixInput.matrix_must_be_square()

**Description:**  
This method verifies whether a given matrix is square, meaning that it has the same number of rows and columns. It is a crucial validation step in matrix operations, as many mathematical operations require square matrices.

**Parameters:**
- None

**Expected Input:**  
- The method expects a matrix-like structure (e.g., a list of lists or a 2D array) to be provided as an attribute of the `MatrixInput` class. The matrix should be a valid representation where each inner list (row) contains the same number of elements (columns).

**Returns:**  
`None`: This method does not return a value. Instead, it raises an exception if the matrix is not square.

**Detailed Logic:**  
- The method checks the dimensions of the matrix by comparing the number of rows to the number of columns.
- If the number of rows does not equal the number of columns, it raises a specific exception indicating that the matrix must be square.
- This validation ensures that any subsequent operations that require a square matrix can be safely performed without encountering dimension-related errors.