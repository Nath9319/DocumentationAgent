# Documentation for `TTestInput`

```markdown
### TTestInput

**Description:**  
The `TTestInput` class serves as a model for conducting an independent t-test. It is responsible for validating that the samples provided for the statistical test are not identical, ensuring that there is sufficient variability in the data for meaningful analysis.

**Parameters/Attributes:**
- `samples` (`list` or `array` of numerical values): A collection of numerical data points that will be used in the t-test. This attribute is essential for the class's functionality, as it holds the input data for statistical analysis.

**Expected Input:**  
- The `samples` attribute should contain at least two distinct numerical values. The class checks for the presence of variability among the samples, which is a prerequisite for performing a valid t-test. If the samples are identical, the class will raise an exception during validation.

**Returns:**  
`None`: The class does not return a value upon instantiation or during its validation process. Instead, it raises exceptions if the input data does not meet the required conditions.

**Detailed Logic:**  
- Upon initialization, the `TTestInput` class stores the provided sample data in its internal state.
- The class includes a validation method, `samples_must_not_be_identical`, which is invoked to check the uniqueness of the samples.
- This method retrieves the samples and converts them into a set to eliminate duplicates. It then assesses the length of the set.
- If the length of the set is less than two, indicating that all samples are identical, an exception is raised to signal that the input is invalid for statistical testing.
- This validation step is crucial, as it ensures that the subsequent statistical analysis can be performed meaningfully, given that identical samples would not provide any information about variability or differences.
```