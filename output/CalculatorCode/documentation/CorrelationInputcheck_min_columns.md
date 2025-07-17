# Documentation for `CorrelationInput.check_min_columns`

### CorrelationInput.check_min_columns(min_columns: int) -> None

**Description:**
The `check_min_columns` method is responsible for validating that the number of columns in a given dataset meets a specified minimum requirement. This method is part of the `CorrelationInput` class and is crucial for ensuring that the data provided for correlation analysis is sufficient to yield meaningful results.

**Parameters:**
- `min_columns` (`int`): The minimum number of columns that the dataset must contain for the correlation analysis to proceed.

**Expected Input:**
- `min_columns` should be a positive integer representing the minimum threshold for the number of columns. If the dataset has fewer columns than this value, the method will raise an exception to indicate that the input is insufficient.

**Returns:**
`None`: This method does not return any value. Instead, it raises an exception if the validation fails.

**Detailed Logic:**
- The method begins by checking the current number of columns in the dataset associated with the `CorrelationInput` instance.
- It compares this number against the `min_columns` parameter.
- If the dataset contains fewer columns than the specified minimum, the method raises a `ValueError`, indicating that the dataset does not meet the required criteria for further processing.
- This validation helps to prevent errors in subsequent operations that rely on having a sufficient number of data points for correlation analysis. The method leverages the `field_validator` function to ensure that the input meets the necessary validation rules, thereby maintaining data integrity throughout the process.

---
*Generated with 100% context confidence*
