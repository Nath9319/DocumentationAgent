# Documentation for `np.median`

### np.median(a: array_like, axis: Optional[int] = None, out: Optional[array] = None, overwrite_input: bool = False, keepdims: bool = False) -> float

**Description:**
Calculates the median of the given array along the specified axis. The median is the value separating the higher half from the lower half of a data sample. This function can handle multi-dimensional arrays and provides options for specifying the axis along which to compute the median.

**Parameters:**
- `a` (`array_like`): The input array or object that can be converted to an array. This is the data from which the median will be computed.
- `axis` (`Optional[int]`): The axis along which the median is computed. By default, the median is computed over the flattened array. If specified, it must be an integer or a tuple of integers.
- `out` (`Optional[array]`): An optional output array to store the result. It must have the same shape as the expected output.
- `overwrite_input` (`bool`, default: `False`): If set to `True`, allows the input array to be modified in place, which can improve performance but may lead to loss of the original data.
- `keepdims` (`bool`, default: `False`): If set to `True`, the reduced axes are retained in the result as dimensions with size one, allowing for easier broadcasting.

**Expected Input:**
- `a` should be an array-like structure (e.g., list, tuple, NumPy array) containing numerical data.
- The `axis` parameter should be an integer or tuple of integers corresponding to the dimensions of the input array.
- The `out` parameter, if provided, should be an array of the appropriate shape to hold the result.
- The `overwrite_input` parameter should be a boolean value.
- The `keepdims` parameter should also be a boolean value.

**Returns:**
`float`: The median value of the input array along the specified axis. If the input is an empty array, the function will return `nan`.

**Detailed Logic:**
- The function first checks the shape of the input array and flattens it if no axis is specified.
- It sorts the values in the specified axis to determine the median. If the number of elements is odd, the median is the middle element; if even, it is the average of the two middle elements.
- If the `overwrite_input` flag is set to `True`, the function may modify the input array to optimize performance.
- The result is returned as a single value or an array, depending on the dimensions of the input and the `keepdims` parameter. If `keepdims` is `True`, the output retains the dimensions of the input array, with reduced axes having a size of one.

---
*Generated with 100% context confidence*
