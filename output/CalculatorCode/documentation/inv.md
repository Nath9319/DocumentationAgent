# Documentation for `inv`

### inv()

**Description:**
The `inv` function is designed to compute the inverse of a given matrix. It is a crucial operation in linear algebra, often used in various mathematical and engineering applications, including solving systems of linear equations, optimization problems, and more.

**Parameters:**
- `matrix` (`List[List[float]]`): A two-dimensional list representing the matrix for which the inverse is to be calculated. The matrix must be square (i.e., the number of rows must equal the number of columns) and non-singular (i.e., it must have a non-zero determinant).

**Expected Input:**
- The input `matrix` should be a square matrix, meaning it has the same number of rows and columns.
- The elements of the matrix should be numerical values (integers or floats).
- The matrix must be non-singular; if the determinant of the matrix is zero, the function will not be able to compute the inverse.

**Returns:**
`List[List[float]]`: A two-dimensional list representing the inverse of the input matrix. If the input matrix is singular, the function may raise an exception or return an error message indicating that the inverse cannot be computed.

**Detailed Logic:**
- The function begins by validating the input to ensure that the matrix is square and non-singular.
- It computes the determinant of the matrix. If the determinant is zero, it raises an error indicating that the matrix does not have an inverse.
- If the determinant is non-zero, the function proceeds to calculate the inverse using an appropriate algorithm, such as Gaussian elimination or the adjugate method.
- The resulting inverse matrix is then returned as a two-dimensional list, maintaining the same structure as the input matrix.
- This function does not rely on any external libraries or modules, but it may implement fundamental linear algebra techniques to achieve its goal.

---
*Generated with 100% context confidence*
