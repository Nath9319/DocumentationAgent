# Documentation for `np.sqrt`

### np.sqrt(x: Union[float, np.ndarray]) -> np.ndarray

**Description:**
Calculates the non-negative square root of a given number or each element in an array. This function is part of the NumPy library, which is widely used for numerical computations in Python. The square root is defined for non-negative inputs, and the function will return complex results for negative inputs if the appropriate data type is specified.

**Parameters:**
- `x` (`Union[float, np.ndarray]`): A non-negative float or an array-like structure containing non-negative values for which the square root is to be computed.

**Expected Input:**
- `x` should be a non-negative float or a NumPy array containing non-negative numbers. If `x` contains negative values, the behavior will depend on the data type of the array. By default, the function will raise a warning and return `nan` for those elements unless the input is explicitly cast to a complex type.

**Returns:**
`np.ndarray`: An array of the same shape as `x`, containing the non-negative square roots of the input values. If `x` is a scalar, the return type will be a scalar as well.

**Detailed Logic:**
- The function first checks the type of the input `x`. If `x` is a scalar, it computes the square root directly.
- If `x` is an array, it applies the square root operation element-wise across the entire array.
- The function uses efficient vectorized operations provided by NumPy, which allows it to handle large datasets quickly and efficiently.
- For negative inputs, the function will return `nan` for those elements unless the input is cast to a complex type, in which case it will return complex square roots.
- The function does not have any internal dependencies and operates solely on the input provided.

---
*Generated with 100% context confidence*
