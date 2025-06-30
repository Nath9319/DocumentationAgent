# Documentation for `matrix_must_be_square`

```python
def matrix_must_be_square(cls, v):
    """
    Validates that the provided matrix is square.

    A square matrix is defined as a matrix with the same number of rows and columns.
    This function checks if the input matrix is empty and raises a ValueError if it is.
    It then verifies that each row in the matrix has the same length as the number of rows.

    Args:
        cls: The class that calls this method (typically used for class methods).
        v (list of list): The matrix to be validated, represented as a list of lists.

    Raises:
        ValueError: If the matrix is empty or if the number of rows does not equal
                    the number of columns.

    Returns:
        list of list: The validated square matrix.

    Example:
        >>> matrix_must_be_square(None, [[1, 2], [3, 4]])
        [[1, 2], [3, 4]]

        >>> matrix_must_be_square(None, [[1, 2], [3]])
        ValueError: Matrix must be square (same number of rows and columns).
    """
    # This validator is called to ensure the matrix is square, a requirement
    # for determinant and inverse calculations. This is a direct link to the
    # logic in the 'stats_service.py'.
    if not v:
        raise ValueError("Matrix cannot be empty.")
    rows = len(v)
    for row in v:
        if len(row) != rows:
            raise ValueError("Matrix must be square (same number of rows and columns).")
    return v
``` 

### Documentation Breakdown:
- **Purpose:** The docstring clearly states the function's purpose, which is to validate that a matrix is square.
- **Arguments:** It specifies the parameters, including the class context and the matrix itself.
- **Exceptions:** It details the conditions under which exceptions are raised, providing clarity on error handling.
- **Return Value:** It describes what the function returns upon successful validation.
- **Examples:** It includes usage examples to illustrate correct and incorrect inputs, enhancing understanding for users.