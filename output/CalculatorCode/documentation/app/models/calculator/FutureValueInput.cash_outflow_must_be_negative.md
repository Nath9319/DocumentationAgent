# Documentation for FutureValueInput.cash_outflow_must_be_negative

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### FutureValueInput.cash_outflow_must_be_negative

**Description:**
The `cash_outflow_must_be_negative` method is a validation function designed to ensure that cash outflow values are represented as negative numbers. This is crucial in financial calculations where cash inflows are typically positive and cash outflows must be negative to maintain accurate financial modeling.

**Parameters/Attributes:**
- None

**Expected Input:**
- The method expects a numeric input that represents a cash flow value. The input should be a float or an integer. The primary constraint is that this value must be negative; if a positive value or zero is provided, the method will raise a `ValueError`.

**Returns:**
- None: The method does not return a value. Instead, it performs validation and raises an exception if the input does not meet the specified criteria.

**Detailed Logic:**
- The method utilizes the `field_validator` from an external library to enforce the validation rule. It checks the provided cash flow value and verifies that it is negative.
- If the value is not negative, a `ValueError` is raised, indicating that the cash outflow must be negative. This ensures that any financial calculations relying on this input will be based on valid data, preventing potential errors in further computations. 
- The method is likely invoked during the initialization or assignment of cash flow attributes within the `FutureValueInput` class, ensuring that all cash outflow values adhere to the expected format before any calculations are performed.

---
*Generated with 0% context confidence*
