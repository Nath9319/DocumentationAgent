# Documentation for `np.abs`

### np.abs(x: Union[int, float, np.ndarray]) -> np.ndarray

**Description:**
The `np.abs` function computes the absolute value of a given input. It can handle various data types, including integers, floats, and NumPy arrays. The function returns the non-negative value of each element in the input, effectively removing any negative signs.

**Parameters:**
- `x` (`Union[int, float, np.ndarray]`): The input value(s) for which the absolute value is to be calculated. This can be a single integer, a float, or a NumPy array containing numeric values.

**Expected Input:**
- The input `x` can be:
  - A single integer or float, which will return its absolute value.
  - A NumPy array of integers or floats, where the function will return an array of the absolute values of each element.
- The function can handle both scalar and array-like inputs, including multi-dimensional arrays.

**Returns:**
`np.ndarray`: An array containing the absolute values of the input elements. If the input is a scalar, the output will be a scalar as well.

**Detailed Logic:**
- The function begins by checking the type of the input `x`. If `x` is a scalar (integer or float), it directly computes and returns its absolute value.
- If `x` is a NumPy array, the function iterates through each element of the array, applying the absolute value operation.
- The result is a new NumPy array containing the absolute values of the original input elements.
- The function is optimized for performance with NumPy arrays, leveraging vectorized operations to efficiently compute absolute values across potentially large datasets without the need for explicit loops.

---
*Generated with 100% context confidence*
