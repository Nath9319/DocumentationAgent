# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### FutureValueInput.cash_outflow_must_be_negative

**Description:**
The `cash_outflow_must_be_negative` method is a validation function designed to ensure that any cash outflow value provided to the `FutureValueInput` class is negative. This is crucial in financial calculations where cash inflows are represented as positive values and cash outflows as negative values. The method raises a `ValueError` if the provided cash outflow does not meet this requirement.

**Parameters/Attributes:**
None.

**Expected Input:**
- The method expects a single input value that represents the cash outflow. This value should be a numeric type (e.g., integer or float).
- The input must be negative; otherwise, a `ValueError` will be raised.

**Returns:**
None. The method does not return a value; it either validates the input or raises an error.

**Detailed Logic:**
- The method utilizes the `field_validator` from an external library to enforce the validation rule.
- When invoked, it checks the value of the cash outflow.
- If the value is not negative, it raises a `ValueError`, indicating that the cash outflow must be a negative number.
- This method is integral to maintaining the integrity of financial data within the `FutureValueInput` class, ensuring that all cash outflows are correctly represented as negative values for further calculations.

---
*Generated with 0% context confidence*
