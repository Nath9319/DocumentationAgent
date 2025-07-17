# Documentation for `np.sqrt`

### np.sqrt(x: Union[int, float, np.ndarray]) -> np.ndarray

**Description:**
Calculates the non-negative square root of a given number or array of numbers. This function is part of the NumPy library and is optimized for performance, allowing for efficient computation over large datasets.

**Parameters:**
- `x` (`Union[int, float, np.ndarray]`): The input value(s) for which the square root is to be calculated. This can be a single integer or float, or a NumPy array containing multiple values.

**Expected Input:**
- `x` should be a non-negative integer, float, or a NumPy array of non-negative numbers. If `x` contains negative values, the function will return `nan` (not a number) for those entries.

**Returns:**
`np.ndarray`: An array containing the square roots of the input values. If the input is a single number, the output will be a scalar value. The output will have the same shape as the input if `x` is an array.

**Detailed Logic:**
- The function first checks the input type to determine if it is a scalar or an array.
- For scalar inputs, it computes the square root directly using the mathematical definition.
- For array inputs, it applies the square root operation element-wise across the entire array, leveraging NumPy's vectorized operations for efficiency.
- The function handles edge cases, such as zero (which returns zero) and negative numbers (which return `nan`).
- The implementation is designed to be fast and efficient, making it suitable for use in scientific computing and data analysis where performance is critical.

---
*Generated with 100% context confidence*
