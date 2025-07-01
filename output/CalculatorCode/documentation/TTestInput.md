# Documentation for `TTestInput`

### TTestInput

**Description:**
`TTestInput` is a model class designed to represent the input data for an independent t-test. It ensures that the samples provided for the test are not identical, which is a prerequisite for conducting a valid t-test. The class leverages validation mechanisms to enforce this constraint.

**Parameters/Attributes:**
- `sample1` (`List[float]`): The first sample of data for the t-test.
- `sample2` (`List[float]`): The second sample of data for the t-test.

**Expected Input:**
- `sample1` and `sample2` should be lists of floats representing numerical data points. 
- Both samples must contain at least one element.
- The two samples must not be identical; if they are, a validation error will be raised.

**Returns:**
`None`: The class does not return a value upon instantiation but raises exceptions if validation fails.

**Detailed Logic:**
- The class inherits from `BaseModel`, which likely provides foundational functionality for data validation and model behavior.
- It utilizes `Field` to define the attributes `sample1` and `sample2`, which are expected to hold the data for the t-test.
- The `field_validator` is employed to implement custom validation logic that checks if the two samples are identical. If they are, a `ValueError` is raised, indicating that the samples must differ for a valid t-test.
- This validation ensures that any instance of `TTestInput` is guaranteed to have valid data before any statistical analysis is performed.