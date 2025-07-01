# Documentation for `CorrelationInput`

### CorrelationInput

**Description:**
`CorrelationInput` is a model class designed to represent and validate the input data for generating a correlation matrix. It ensures that the input consists of at least two columns when specified, thereby enforcing the necessary conditions for correlation analysis.

**Parameters/Attributes:**
- **None**: The class does not take any parameters upon instantiation. It relies on internal validation mechanisms to ensure the integrity of the data it processes.

**Expected Input:**
- The class expects input data structured in a way that can be interpreted as a matrix (e.g., a DataFrame or similar structure). Specifically, it requires at least two columns to perform correlation calculations. If the input does not meet this criterion, a validation error will be raised.

**Returns:**
- **None**: The class does not return a value upon instantiation. Instead, it validates the input data and may raise exceptions if the validation fails.

**Detailed Logic:**
- Upon initialization, `CorrelationInput` leverages the `BaseModel` class, which likely provides foundational functionality for data modeling and validation.
- The class utilizes the `field_validator` to enforce the requirement that at least two columns must be present in the input data. This validation is crucial for ensuring that correlation calculations can be performed meaningfully.
- If the input data does not meet the specified conditions, a `ValueError` is raised, indicating that the input is invalid. This mechanism helps maintain data integrity and prevents errors during subsequent analysis steps.