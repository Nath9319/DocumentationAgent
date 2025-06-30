# Documentation for `calculate_inverse`

```python
def calculate_inverse(self, matrix: List[List[float]]) -> List[List[float]]:
    """Calculates the inverse of a square matrix.

    This function takes a square matrix as input and returns its inverse. 
    If the matrix is singular (i.e., it does not have an inverse), a 
    DataError is raised.

    Args:
        matrix (List[List[float]]): A square matrix represented as a 
        list of lists, where each inner list corresponds to a row of the 
        matrix and contains float values.

    Returns:
        List[List[float]]: The inverse of the input matrix, represented 
        as a list of lists.

    Raises:
        DataError: If the input matrix is singular and cannot be inverted.

    Example:
        >>> calc = Calculator()
        >>> matrix = [[1, 2], [3, 4]]
        >>> calc.calculate_inverse(matrix)
        [[-2.0, 1.0], [1.5, -0.5]]
    """
    np_matrix = np.array(matrix)
    try:
        inverse_matrix = np.linalg.inv(np_matrix)
        return inverse_matrix.tolist()
    except np.linalg.LinAlgError:
        raise DataError("Matrix is singular and cannot be inverted.")
``` 

### Documentation Breakdown:
- **Function Purpose:** Clearly states what the function does—calculates the inverse of a square matrix.
- **Arguments:** Describes the input parameter, including its type and structure.
- **Returns:** Specifies the output of the function, including its type.
- **Raises:** Details the exception that may be raised under certain conditions.
- **Example:** Provides a practical example of how to use the function, enhancing user understanding.