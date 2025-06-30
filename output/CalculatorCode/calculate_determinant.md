# Documentation for `calculate_determinant`

```python
def calculate_determinant(self, matrix: List[List[float]]) -> float:
    """Calculates the determinant of a square matrix.

    This function takes a square matrix as input and computes its determinant using NumPy's 
    linear algebra module. The input matrix must be two-dimensional and have the same number 
    of rows and columns. If the input does not meet these criteria, a DataError is raised.

    Args:
        matrix (List[List[float]]): A square matrix represented as a list of lists, where 
                                     each inner list corresponds to a row of the matrix.

    Returns:
        float: The determinant of the input square matrix.

    Raises:
        DataError: If the input matrix is not square (i.e., the number of rows does not equal 
                   the number of columns) or if the input is not a two-dimensional list.

    Example:
        >>> calc = Calculator()
        >>> matrix = [[1, 2], [3, 4]]
        >>> determinant = calc.calculate_determinant(matrix)
        >>> print(determinant)
        -2.0
    """
    np_matrix = np.array(matrix)
    if np_matrix.ndim != 2 or np_matrix.shape[0] != np_matrix.shape[1]:
        raise DataError("Input must be a square matrix.")
    return np.linalg.det(np_matrix)
``` 

### Documentation Breakdown:
- **Function Purpose:** Clearly states that the function calculates the determinant of a square matrix.
- **Arguments:** Describes the expected input format and type.
- **Returns:** Specifies the output type and what it represents.
- **Raises:** Details the conditions under which an error will be raised, enhancing robustness.
- **Example:** Provides a practical example of how to use the function, making it easier for users to understand its application.