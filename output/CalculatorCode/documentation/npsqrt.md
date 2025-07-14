# Documentation for `np.sqrt`

### np.sqrt(x: Union[float, np.ndarray]) -> np.ndarray

**Description:**
Calculates the non-negative square root of a given number or array of numbers. This function is part of the NumPy library and is optimized for performance, allowing for element-wise operations on arrays.

**Parameters:**
- `x` (`Union[float, np.ndarray]`): A non-negative number or an array of non-negative numbers for which the square root is to be computed.

**Expected Input:**
- `x` should be a non-negative float or a NumPy array containing non-negative floats. If `x` contains negative values, the function will return `nan` (not a number) for those elements.

**Returns:**
`np.ndarray`: An array of the same shape as `x`, containing the square roots of the input values. If the input is a single float, the output will be a float.

**Detailed Logic:**
- The function first checks the input type. If `x` is a single float, it computes the square root directly.
- If `x` is a NumPy array, it performs an element-wise operation to compute the square root for each element in the array.
- The function leverages NumPy's underlying optimized C implementations for efficient computation, ensuring that the operation is performed quickly even for large datasets.
- In cases where the input contains negative values, the function will return `nan` for those specific elements, adhering to the mathematical definition of square roots.

---
*Generated with 100% context confidence*
