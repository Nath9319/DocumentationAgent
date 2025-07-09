# Documentation for `CorrelationInput.check_min_columns`

### CorrelationInput.check_min_columns() -> None

**Description:**
The `check_min_columns` method is responsible for validating that the minimum number of columns required for a correlation operation is present in the input data. This method ensures that the data structure meets the necessary criteria before any further processing occurs, thereby preventing potential errors that could arise from insufficient data.

**Parameters:**
None

**Expected Input:**
- The method is expected to operate on an instance of the `CorrelationInput` class, which should contain data structured in a way that can be evaluated for the number of columns.
- The method does not take any direct input parameters but relies on the internal state of the `CorrelationInput` instance.

**Returns:**
None

**Detailed Logic:**
- The method first retrieves the current data structure associated with the `CorrelationInput` instance.
- It then checks the number of columns present in this data structure against a predefined minimum threshold.
- If the number of columns is below the required minimum, the method raises a `ValueError`, indicating that the input data does not meet the necessary criteria for processing.
- This validation is crucial for ensuring that subsequent operations that depend on a sufficient number of columns can be executed without encountering errors. The method leverages the `field_validator` function to perform this check, ensuring that the validation logic is consistent and reusable across different contexts within the application.

---
*Generated with 100% context confidence*
