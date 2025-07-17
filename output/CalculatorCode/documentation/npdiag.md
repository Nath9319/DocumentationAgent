# Documentation for `np.diag`

### np.diag(v, k=0)

**Description:**
The `np.diag` function is used to create a diagonal array or extract the diagonal from an existing array. When provided with a one-dimensional array, it generates a two-dimensional array with the elements of the input array placed along the specified diagonal. Conversely, when given a two-dimensional array, it returns the elements of the specified diagonal as a one-dimensional array.

**Parameters:**
- `v` (`array_like`): The input array from which to create a diagonal or from which to extract a diagonal. This can be either a one-dimensional or two-dimensional array.
- `k` (`int`, optional): The diagonal in question. The default value is `0`, which refers to the main diagonal. A positive value indicates an upper diagonal, while a negative value indicates a lower diagonal.

**Expected Input:**
- `v` should be a one-dimensional array (e.g., a list or a NumPy array) to create a diagonal matrix or a two-dimensional array to extract a diagonal.
- `k` should be an integer, which can be negative, zero, or positive, indicating the desired diagonal.

**Returns:**
- `ndarray`: If `v` is a one-dimensional array, it returns a two-dimensional array with the input array's elements on the specified diagonal. If `v` is a two-dimensional array, it returns a one-dimensional array containing the elements of the specified diagonal.

**Detailed Logic:**
- If the input `v` is a one-dimensional array, the function initializes a square two-dimensional array of zeros with dimensions based on the length of `v`. It then places the elements of `v` along the diagonal specified by `k`.
- If the input `v` is a two-dimensional array, the function retrieves the elements from the diagonal specified by `k` and returns them as a one-dimensional array.
- The function handles various shapes and sizes of input arrays and ensures that the diagonal extraction or creation is performed correctly based on the specified diagonal index `k`. It does not rely on any external modules but utilizes NumPy's array manipulation capabilities.

---
*Generated with 100% context confidence*
