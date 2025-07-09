# Documentation for `round`

### round(value: float, ndigits: Optional[int] = None) -> float

**Description:**
The `round` function rounds a floating-point number to a specified number of decimal places. If no number of decimal places is specified, it rounds to the nearest integer. This function is commonly used to simplify numerical data for display or further calculations.

**Parameters:**
- `value` (`float`): The floating-point number that needs to be rounded.
- `ndigits` (`Optional[int]`): The number of decimal places to round to. If omitted or set to `None`, the function rounds to the nearest integer.

**Expected Input:**
- `value` should be a valid floating-point number.
- `ndigits`, if provided, should be a non-negative integer. If `ndigits` is negative, it rounds to the left of the decimal point.

**Returns:**
`float`: The rounded value of the input number, either as an integer or a floating-point number with the specified number of decimal places.

**Detailed Logic:**
- The function first checks the value of `ndigits`. If it is `None`, the function rounds `value` to the nearest integer using standard rounding rules (i.e., values exactly halfway between two integers are rounded to the nearest even integer).
- If `ndigits` is specified, the function calculates the rounding factor based on the power of 10 corresponding to `ndigits` and applies the rounding logic accordingly.
- The function handles edge cases, such as rounding negative numbers and rounding values with a large number of decimal places.
- The `round` function does not rely on any external modules or dependencies, performing its operations using basic arithmetic.

---
*Generated with 100% context confidence*
