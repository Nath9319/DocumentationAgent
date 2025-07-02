# Documentation for `CorrelationInput`

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### CorrelationInput

**Description:**
The `CorrelationInput` class serves as a model for managing and validating a correlation matrix. It ensures that the input data contains at least two columns when specified, thereby facilitating the computation of correlations between multiple variables.

**Parameters/Attributes:**
- `data` (`list` or `DataFrame`): The input data that is expected to contain multiple columns for correlation analysis.
- `min_columns` (`int`): An optional attribute that specifies the minimum number of columns required. If set, the class will validate that the input data meets this requirement.

**Expected Input:**
- The `data` parameter should be a list or a DataFrame containing numerical values organized in columns. 
- If `min_columns` is specified, it must be a positive integer indicating the minimum number of columns that the input data must have. The class will raise a `ValueError` if the input does not meet this requirement.

**Returns:**
`None`: The class does not return any value upon instantiation. It is designed to validate the input data and may raise exceptions if validation fails.

**Detailed Logic:**
- Upon initialization, the `CorrelationInput` class checks the structure of the provided `data`. If `min_columns` is specified, it verifies that the number of columns in `data` is at least equal to `min_columns`.
- If the validation fails (i.e., the number of columns is less than the specified minimum), a `ValueError` is raised, indicating that the input does not meet the required criteria.
- The class leverages the `BaseModel` for foundational functionality and utilizes `field_validator` to enforce input validation rules, ensuring that the data integrity is maintained throughout its usage.

---
*Generated with 0% context confidence*
