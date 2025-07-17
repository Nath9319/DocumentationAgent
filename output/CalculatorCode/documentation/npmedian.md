# Documentation for `np.median`

### np.median(a: array_like, axis: Optional[int] = None, out: Optional[ndarray] = None, overwrite_input: bool = False, keepdims: bool = False) -> float

**Description:**
Calculates the median of the given array along the specified axis. The median is the value separating the higher half from the lower half of the data sample. This function can handle multi-dimensional arrays and provides options for output formatting and handling of input data.

**Parameters:**
- `a` (`array_like`): The input array or object that can be converted to an array. This is the dataset from which the median will be calculated.
- `axis` (`Optional[int]`): The axis along which the median is computed. By default, the median is computed over the flattened array. If an integer is provided, the median is calculated along that specific axis.
- `out` (`Optional[ndarray]`): An optional output array to store the result. If provided, it must have the same shape as the expected output.
- `overwrite_input` (`bool`, default: `False`): If set to `True`, allows the input array to be modified in place to save memory. This can lead to loss of the original data.
- `keepdims` (`bool`, default: `False`): If set to `True`, the reduced axes are left in the result as dimensions with size one, allowing for broadcasting.

**Expected Input:**
- `a` should be an array-like structure (e.g., list, tuple, or NumPy array) containing numerical data.
- The `axis` parameter should be an integer or `None`. If an integer is provided, it must be within the bounds of the dimensions of `a`.
- The `out` parameter, if used, should be a NumPy array of the appropriate shape.
- `overwrite_input` should be a boolean value.
- `keepdims` should also be a boolean value.

**Returns:**
`float`: The median value(s) of the input array. If the input is multi-dimensional and `axis` is specified, the return type will be an array of medians along the specified axis.

**Detailed Logic:**
- The function begins by validating the input array `a`, ensuring it can be converted to a NumPy array.
- If `axis` is specified, the function computes the median along that axis, otherwise, it flattens the array and computes the median of all elements.
- The function handles special cases, such as when the input array is empty or contains NaN values, by returning NaN or the appropriate median value.
- If `overwrite_input` is set to `True`, the function may modify the input array to optimize memory usage.
- The result is computed using efficient algorithms that ensure the median is found in a time-efficient manner, typically involving sorting or partitioning methods.
- The `keepdims` parameter allows the output to retain the original dimensions of the input array, facilitating further operations that require consistent array shapes.

---
*Generated with 100% context confidence*
