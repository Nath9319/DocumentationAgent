# Documentation for `MatrixInput.matrix_must_be_square`

### MatrixInput.matrix_must_be_square() -> None

**Description:**
This method validates that a given matrix is square, meaning it has the same number of rows and columns. It is typically used in contexts where square matrices are required for mathematical operations, such as matrix inversion or certain algorithms in linear algebra.

**Parameters:**
None

**Expected Input:**
- The method expects a matrix-like structure (e.g., a list of lists or a 2D array) to be passed implicitly through the context in which this method is invoked. The matrix should be a collection of collections, where each inner collection represents a row of the matrix.

**Returns:**
None

**Detailed Logic:**
- The method utilizes a `field_validator` to enforce the validation rule that the matrix must be square.
- It checks the length of the outer list (representing the number of rows) and compares it to the length of each inner list (representing the number of columns).
- If the number of rows does not equal the number of columns, a `ValueError` is raised, indicating that the matrix is not square.
- This validation ensures that any subsequent operations that require a square matrix can proceed without errors related to matrix dimensions.