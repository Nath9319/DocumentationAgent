# Documentation for `MatrixInput.matrix_must_be_square`

```python
@field_validator('matrix')
@classmethod
def matrix_must_be_square(cls, v):
    """
    Validates that the provided matrix is square.

    A square matrix is defined as a matrix with the same number of rows and columns.
    This method checks if the input matrix is not empty and raises a ValueError if it is.
    It then verifies that each row in the matrix has the same length as the number of rows.

    Args:
        cls: The class that this method is bound to.
        v (list of list): The matrix to be validated.

    Raises:
        ValueError: If the matrix is empty or if it is not square (i.e., 
                     if any row does not have the same number of elements as the number of rows).

    Returns:
        list of list: The validated square matrix.

    Example:
        >>> MatrixInput.matrix_must_be_square([[1, 2], [3, 4]])
        [[1, 2], [3, 4]]

        >>> MatrixInput.matrix_must_be_square([[1, 2], [3]])
        ValueError: Matrix must be square (same number of rows and columns).
    """
    if not v:
        raise ValueError('Matrix cannot be empty.')
    rows = len(v)
    for row in v:
        if len(row) != rows:
            raise ValueError('Matrix must be square (same number of rows and columns).')
    return v
``` 

### Documentation Breakdown:
- **Purpose:** The docstring clearly states the purpose of the method, which is to validate that a matrix is square.
- **Arguments:** It specifies the parameters, including the class reference and the matrix itself.
- **Exceptions:** It details the conditions under which exceptions are raised, providing clarity on error handling.
- **Return Value:** It describes what the method returns if the validation is successful.
- **Examples:** It includes usage examples to illustrate how the method works and the expected outcomes, enhancing understanding for users.