# Documentation for `MatrixInput`

```python
class MatrixInput(BaseModel):
    """
    Model for matrix operations.

    This class represents a matrix and includes validation to ensure that the matrix is square.
    It also provides a method to convert the matrix into a NumPy array for further numerical operations.

    Attributes:
        matrix (List[List[float]]): A two-dimensional list representing the matrix. 
                                     Must be square (same number of rows and columns) and cannot be empty.

    Methods:
        matrix_must_be_square(cls, v):
            Validates that the provided matrix is square.
        
        to_numpy_array() -> np.ndarray:
            Converts the matrix stored in the MatrixInput instance to a NumPy array.
    """

    matrix: List[List[float]] = Field(..., min_length=1)

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

    def to_numpy_array(self) -> np.ndarray:
        """
        Converts the matrix stored in the MatrixInput instance to a NumPy array.

        Returns:
            np.ndarray: A NumPy array representation of the matrix.

        Example:
            matrix_input = MatrixInput([[1, 2], [3, 4]])
            numpy_array = matrix_input.to_numpy_array()
            # numpy_array will be: array([[1, 2], [3, 4]])
        """
        return np.array(self.matrix)
``` 

### Summary of Documentation:
- **Purpose**: The `MatrixInput` class serves as a model for matrix operations, ensuring that the matrix is square and providing functionality to convert it to a NumPy array.
- **Attributes**: The class has a single attribute, `matrix`, which is validated to be a non-empty square matrix.
- **Methods**: It includes a class method for validating the matrix and an instance method for conversion to a NumPy array, both of which are documented with clear descriptions, argument specifications, return types, and usage examples.