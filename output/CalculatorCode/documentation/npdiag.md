# Documentation for `np.diag`

### np.diag(v, k=0)

**Description:**
The `np.diag` function is used to create a diagonal array from a given input array or to extract the diagonal elements from a 2D array. When provided with a 1D array, it generates a square matrix with the elements of the array placed on the specified diagonal. If given a 2D array, it returns the elements along the specified diagonal.

**Parameters:**
- `v` (`array_like`): The input array from which to create a diagonal array or from which to extract diagonal elements. This can be either a 1D or 2D array.
- `k` (`int`, optional): The diagonal in which to place the elements. The default value is `0`, which refers to the main diagonal. Positive values refer to diagonals above the main diagonal, while negative values refer to those below.

**Expected Input:**
- `v` can be a 1D array (e.g., a list or a NumPy array) or a 2D array (e.g., a matrix).
- If `v` is a 1D array, it should contain numeric values.
- If `v` is a 2D array, it should be structured such that it can form a square matrix when the diagonal is created.
- The parameter `k` should be an integer, and it can be negative, zero, or positive.

**Returns:**
`ndarray`: The function returns a 2D array (matrix) if `v` is a 1D array, or a 1D array containing the diagonal elements if `v` is a 2D array. The shape of the returned array depends on the input and the specified diagonal.

**Detailed Logic:**
- If the input `v` is a 1D array, the function initializes a square matrix of size equal to the length of `v`, filling the specified diagonal (determined by `k`) with the elements of `v`.
- If the input `v` is a 2D array, the function extracts the elements along the specified diagonal. The extraction is based on the index offset defined by `k`, where the main diagonal corresponds to `k=0`.
- The function handles the creation of the diagonal matrix or extraction of diagonal elements efficiently, leveraging NumPy's array manipulation capabilities.
- This function does not have any internal dependencies and operates solely on the input provided.

---
*Generated with 100% context confidence*
