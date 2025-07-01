# Documentation for `MatrixInput`

### MatrixInput

**Description:**
The `MatrixInput` class serves as a model for performing various matrix operations. It incorporates validation mechanisms to ensure that the input matrices conform to specified requirements, and it includes a helper function to facilitate matrix-related tasks.

**Parameters/Attributes:**
- `matrix` (`np.array`): A NumPy array representing the matrix input. This attribute is subject to validation to ensure it meets the necessary criteria for matrix operations.
- `rows` (`int`): An integer representing the number of rows in the matrix. This is derived from the shape of the input matrix.
- `columns` (`int`): An integer representing the number of columns in the matrix. This is also derived from the shape of the input matrix.

**Expected Input:**
- The `matrix` attribute must be a valid NumPy array. It should be two-dimensional, meaning it must have at least one row and one column.
- The input matrix should not contain any invalid values (e.g., NaN or infinite values) as these would violate the validation rules.

**Returns:**
`None`: The class does not return a value upon instantiation. Instead, it initializes the matrix and its attributes based on the provided input.

**Detailed Logic:**
- Upon instantiation, the `MatrixInput` class validates the input matrix using the `field_validator` decorator, which checks for conditions such as dimensionality and value integrity.
- The `rows` and `columns` attributes are automatically set based on the shape of the input matrix, allowing for easy access to the matrix's dimensions.
- The class may include additional methods for performing operations on the matrix, leveraging the capabilities of NumPy for efficient computation.
- The `BaseModel` is likely extended to provide foundational functionality, while the `Field` and `field_validator` are used to manage and validate the attributes effectively.