# Documentation for `round`

### round(value: float, ndigits: Optional[int] = None) -> float

**Description:**
The `round` function rounds a floating-point number to a specified number of decimal places. If no number of decimal places is specified, it rounds to the nearest integer. This function is commonly used to control the precision of numerical outputs, making it easier to present data in a more readable format.

**Parameters:**
- `value` (`float`): The floating-point number that needs to be rounded.
- `ndigits` (`Optional[int]`): The number of decimal places to round to. If omitted or set to `None`, the function will round to the nearest integer.

**Expected Input:**
- `value` should be a valid floating-point number (positive, negative, or zero).
- `ndigits`, if provided, should be a non-negative integer. If it is negative, it indicates rounding to the left of the decimal point.

**Returns:**
`float`: The rounded value of the input number, either as an integer (if `ndigits` is `None`) or as a floating-point number with the specified number of decimal places.

**Detailed Logic:**
- The function first evaluates the `ndigits` parameter. If it is `None`, the function rounds the `value` to the nearest integer using standard rounding rules (i.e., values exactly halfway between two integers are rounded to the nearest even integer).
- If `ndigits` is specified, the function calculates the rounding factor based on the power of ten corresponding to `ndigits`. It then applies this factor to the `value` to perform the rounding operation.
- The function does not rely on any external dependencies and performs the rounding operation using basic arithmetic and built-in rounding logic.

---
*Generated with 100% context confidence*
