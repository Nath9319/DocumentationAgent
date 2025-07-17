# Documentation for `TTestInput`

### TTestInput

**Description:**
`TTestInput` is a model class designed to represent the input data required for conducting an independent t-test. It ensures that the samples provided for the test are not identical, thereby validating the assumptions necessary for the statistical analysis to be meaningful.

**Parameters/Attributes:**
- `sample1` (`List[float]`): The first sample of data for the t-test.
- `sample2` (`List[float]`): The second sample of data for the t-test.

**Expected Input:**
- `sample1` and `sample2` should be lists of floating-point numbers representing the data points for each sample.
- Both samples must contain at least one data point, and they must not be identical (i.e., they should have different values).

**Returns:**
`None`: The class does not return a value upon instantiation but initializes an object representing the input for the t-test.

**Detailed Logic:**
- Upon instantiation, `TTestInput` validates that the two samples are not identical. This is crucial for the independent t-test, which assumes that the samples come from different populations.
- The class may utilize the `Field` class to define its attributes, ensuring that the data types and validation rules are correctly applied to the samples.
- If the samples are found to be identical during validation, a `ValueError` is raised, indicating that the input does not meet the necessary criteria for conducting a t-test.
- The class inherits from `BaseModel`, allowing it to leverage any shared functionality or attributes defined in the base class, although `BaseModel` itself does not impose any specific logic or constraints.

---
*Generated with 100% context confidence*
