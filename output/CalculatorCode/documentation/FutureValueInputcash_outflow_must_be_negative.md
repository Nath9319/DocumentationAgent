# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

### FutureValueInput.cash_outflow_must_be_negative(value: Any) -> bool

**Description:**
The `cash_outflow_must_be_negative` method validates that the cash outflow value provided is negative. This is crucial for financial calculations where cash outflows (expenses) are represented as negative values to differentiate them from cash inflows (income), which are positive.

**Parameters:**
- `value` (`Any`): The value representing the cash outflow that needs to be validated.

**Expected Input:**
- `value` should be a numeric type (e.g., integer or float) that represents the cash outflow amount. The method expects this value to be negative to be considered valid.

**Returns:**
`bool`: Returns `True` if the provided cash outflow value is negative; otherwise, it returns `False`.

**Detailed Logic:**
- The method utilizes the `field_validator` function to perform the validation. It checks if the `value` is less than zero, which is the primary condition for a valid cash outflow.
- If the value meets this condition, the method returns `True`, indicating that the cash outflow is valid. If the value is zero or positive, it returns `False`, signaling that the cash outflow must be negative to be acceptable.
- This method is essential for maintaining the integrity of financial calculations within the application, ensuring that cash flows are correctly classified.

---
*Generated with 100% context confidence*
