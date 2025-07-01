# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

### FutureValueInput.cash_outflow_must_be_negative

**Description:**
This method serves as a validation check to ensure that cash outflow values are represented as negative numbers. It is a crucial part of the input validation process within the `FutureValueInput` class, ensuring that any cash outflow entered adheres to the expected financial conventions.

**Parameters/Attributes:**
None

**Expected Input:**
- The method is expected to validate a cash outflow value, which should be a numeric type (e.g., integer or float).
- The method enforces that this value must be negative, reflecting the standard practice in financial calculations where outflows are represented as negative figures.

**Returns:**
- None: The method does not return a value. Instead, it raises an exception if the validation fails.

**Detailed Logic:**
- The method utilizes the `field_validator` to perform the validation check. This is likely part of a data validation framework that ensures input values meet specific criteria.
- If the cash outflow value is not negative, the method raises a `ValueError`, indicating that the input is invalid. This exception handling is crucial for maintaining data integrity and preventing erroneous calculations in subsequent financial operations.
- The method is designed to be invoked during the input processing phase, ensuring that any cash outflow values are validated before further computations are performed.