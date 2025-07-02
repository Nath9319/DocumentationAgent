# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### FutureValueInput.cash_outflow_must_be_negative

**Description:**
This method serves as a validation check to ensure that cash outflow values are represented as negative numbers. It is a critical part of the input validation process for financial calculations, specifically within the context of future value calculations. By enforcing this rule, the method helps prevent logical errors that could arise from incorrectly formatted cash flow inputs.

**Parameters/Attributes:**
None

**Expected Input:**
The method expects a cash outflow value, which should be a numeric type (e.g., integer or float). The value must be negative to comply with the financial logic of cash flows, where outflows are represented as negative amounts.

**Returns:**
None

**Detailed Logic:**
- The method utilizes the `field_validator` from an external library to enforce the validation rule.
- When invoked, it checks the provided cash outflow value.
- If the value is not negative, the method raises a `ValueError`, indicating that the cash outflow must be negative.
- This validation ensures that any financial calculations relying on this input will operate under the correct assumptions regarding cash flow direction.

---
*Generated with 0% context confidence*
