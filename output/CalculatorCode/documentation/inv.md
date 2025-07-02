# Documentation for `inv`

### inv()

**Description:**
The `inv` function is designed to compute the inverse of a given matrix. It is a crucial operation in linear algebra, often used in various mathematical and engineering applications, including solving systems of equations, optimization problems, and more.

**Parameters:**
- `matrix` (`List[List[float]]`): A two-dimensional list representing the matrix for which the inverse is to be calculated. The matrix must be square (i.e., the number of rows must equal the number of columns) and non-singular (i.e., it must have a non-zero determinant).

**Expected Input:**
- The input `matrix` should be a square matrix represented as a list of lists, where each inner list corresponds to a row of the matrix.
- The matrix must be non-singular; otherwise, the function will raise an error. This means that the determinant of the matrix should not be zero.

**Returns:**
`List[List[float]]`: The inverse of the input matrix, represented as a two-dimensional list. If the input matrix is singular, the function will not return a value but will instead raise an exception.

**Detailed Logic:**
- The function begins by validating the input to ensure that the matrix is square and non-singular.
- It calculates the determinant of the matrix. If the determinant is zero, an exception is raised, indicating that the matrix cannot be inverted.
- If the determinant is non-zero, the function proceeds to compute the inverse using a suitable algorithm, such as Gaussian elimination or the adjugate method.
- The resulting inverse matrix is then returned as a two-dimensional list.
- The function does not rely on any external dependencies, making it self-contained for matrix inversion operations.

---
*Generated with 100% context confidence*
