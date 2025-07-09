# Documentation for `inv`

### inv

**Description:**
The `inv` function is designed to compute the inverse of a given matrix. It takes a square matrix as input and returns its inverse, which is a fundamental operation in linear algebra often used in various applications such as solving systems of equations, optimization problems, and more.

**Parameters:**
- `matrix` (`List[List[float]]`): A square matrix represented as a list of lists, where each inner list corresponds to a row of the matrix.

**Expected Input:**
- The input `matrix` must be a square matrix (i.e., the number of rows must equal the number of columns).
- Each element of the matrix should be a float or an integer.
- The matrix must be non-singular, meaning it must have a non-zero determinant; otherwise, the inverse does not exist.

**Returns:**
`List[List[float]]`: The inverse of the input matrix, represented as a list of lists. If the matrix is singular, the function may raise an exception or return an error indication.

**Detailed Logic:**
- The function first verifies that the input is a square matrix by checking the dimensions of the matrix.
- It then calculates the determinant of the matrix. If the determinant is zero, the function raises an error indicating that the matrix is singular and does not have an inverse.
- If the determinant is non-zero, the function proceeds to compute the inverse using an appropriate algorithm, such as Gaussian elimination or the adjugate method.
- Finally, the computed inverse matrix is returned as a list of lists, maintaining the same structure as the input matrix. 

This function does not have any internal dependencies and operates solely on the provided input matrix.

---
*Generated with 100% context confidence*
