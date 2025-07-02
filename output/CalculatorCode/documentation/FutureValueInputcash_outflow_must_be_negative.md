# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

### FutureValueInput.cash_outflow_must_be_negative()

**Description:**
The `cash_outflow_must_be_negative` method is responsible for validating that cash outflow values are negative. This is crucial in financial calculations where cash inflows and outflows are tracked, ensuring that outflows are represented correctly as negative values to maintain the integrity of financial computations.

**Parameters:**
- `value` (`Any`): The cash flow value that needs to be validated as negative.

**Expected Input:**
- `value` should be a numeric type (e.g., integer or float) representing the cash flow amount. The method expects this value to be negative, as positive values would indicate cash inflows, which are not acceptable in this context.

**Returns:**
`None`: The method does not return a value. Instead, it raises a `ValueError` if the validation fails.

**Detailed Logic:**
- The method begins by checking the provided `value` to determine if it is negative.
- If the `value` is not negative, a `ValueError` is raised, indicating that cash outflows must be represented as negative values.
- This method utilizes the `field_validator` function to enforce the validation rule, ensuring that the input adheres to the specified criteria for cash outflows.
- The validation process is essential for maintaining data integrity in financial calculations, preventing erroneous data from being processed further.

---
*Generated with 100% context confidence*
