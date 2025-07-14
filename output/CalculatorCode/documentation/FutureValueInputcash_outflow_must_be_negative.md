# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

### FutureValueInput.cash_outflow_must_be_negative()

**Description:**
The `cash_outflow_must_be_negative` method is responsible for validating that cash outflow values are negative. This is crucial in financial calculations where outflows (expenses) must be represented as negative values to ensure accurate computations of future value.

**Parameters/Attributes:**
- `field_name` (`str`): The name of the field being validated, which should represent the cash outflow.
- `value` (`Any`): The value of the cash outflow that needs to be validated.
- `validation_rules` (`dict`): A dictionary containing the validation rules that the value must satisfy, specifically ensuring that the cash outflow is negative.

**Expected Input:**
- `field_name` should be a string that identifies the cash outflow field.
- `value` can be of any type but is expected to be a numeric type (e.g., `int` or `float`) that represents the cash outflow amount.
- `validation_rules` should include a rule that checks if the value is negative.

**Returns:**
`bool`: Returns `True` if the cash outflow value is negative, indicating that it meets the validation criteria; otherwise, it returns `False`.

**Detailed Logic:**
- The method utilizes the `field_validator` function to perform the validation. It checks if the `value` provided for the cash outflow is negative.
- If the value is not negative, the method will return `False`, indicating that the validation has failed.
- This method is essential for maintaining data integrity in financial calculations, as it ensures that cash outflows are correctly represented in the system.
- If the validation passes, the method returns `True`, allowing further processing of the cash outflow value in financial computations.

---
*Generated with 100% context confidence*
