# Documentation for `round`

### round(number: float, ndigits: Optional[int] = None) -> float

**Description:**
The `round` function rounds a floating-point number to a specified number of decimal places. If no number of decimal places is specified, it rounds to the nearest integer. This function is commonly used to simplify numerical values for display or further calculations.

**Parameters:**
- `number` (`float`): The floating-point number that you want to round.
- `ndigits` (`Optional[int]`): The number of decimal places to round to. If omitted or set to `None`, the function rounds to the nearest integer.

**Expected Input:**
- `number` should be a valid floating-point number (e.g., `3.14159`).
- `ndigits`, if provided, should be a non-negative integer. If `ndigits` is negative, it will round to the left of the decimal point.

**Returns:**
`float`: The rounded value of the input number, either as an integer or a floating-point number with the specified number of decimal places.

**Detailed Logic:**
- The function first checks the value of `ndigits`. If it is `None`, the function rounds the `number` to the nearest integer using standard rounding rules (i.e., values of .5 and above are rounded up).
- If `ndigits` is specified, the function calculates the rounding factor based on the value of `ndigits`. It then applies the rounding logic to the `number` by scaling it, rounding it, and then scaling it back to the desired precision.
- The function handles edge cases, such as rounding halfway cases, according to the IEEE 754 standard, ensuring consistent and predictable results.
- This function does not rely on any external dependencies and performs its operations using basic arithmetic and rounding principles.

---
*Generated with 100% context confidence*
