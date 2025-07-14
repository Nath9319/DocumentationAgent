# Documentation for `np.diag`

### np.diag(v, k=0)

**Description:**
The `np.diag` function is used to create a diagonal array or extract the diagonal from an existing array. When given a 1D array, it constructs a 2D array with the elements of the input array placed along the specified diagonal. Conversely, when provided with a 2D array, it returns the elements of the specified diagonal as a 1D array.

**Parameters:**
- `v` (`array_like`): The input array from which to create a diagonal or from which to extract a diagonal. This can be a 1D or 2D array.
- `k` (`int`, optional): The diagonal in the input array to extract or create. The default value is `0`, which refers to the main diagonal. Positive values refer to diagonals above the main diagonal, while negative values refer to those below.

**Expected Input:**
- `v` should be an array-like structure, which can be a list, tuple, or a NumPy array. If `v` is a 1D array, it should contain numerical values. If `v` is a 2D array, it should be a rectangular array (i.e., all rows must have the same number of columns).
- `k` should be an integer, which can be positive, negative, or zero.

**Returns:**
- `ndarray`: If `v` is a 1D array, the function returns a 2D array with the input array's elements on the specified diagonal. If `v` is a 2D array, it returns a 1D array containing the elements of the specified diagonal.

**Detailed Logic:**
- If the input `v` is a 1D array, the function initializes a square 2D array of shape `(n, n)`, where `n` is the length of the input array. It then places the elements of `v` along the diagonal specified by `k`.
- If the input `v` is a 2D array, the function retrieves the elements from the diagonal specified by `k` using array indexing.
- The function handles various shapes and sizes of input arrays, ensuring that the output is appropriately shaped based on the input type.
- This function does not rely on any external modules but utilizes NumPy's array manipulation capabilities to achieve its functionality.

---
*Generated with 100% context confidence*
