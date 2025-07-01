# Documentation for `TTestInput.samples_must_not_be_identical`

```markdown
### TTestInput.samples_must_not_be_identical()

**Description:**  
This method is designed to validate that the samples provided for a statistical test are not identical. It ensures that the input data for the test contains variability, which is crucial for the validity of statistical analyses.

**Parameters:**  
None

**Expected Input:**  
- The method operates on the internal state of the `TTestInput` class, which is expected to contain sample data. The samples should be a collection (e.g., list, array) of numerical values. The method checks that there are at least two distinct values among the samples to proceed with the statistical test.

**Returns:**  
`None`: This method does not return a value. Instead, it raises an exception if the samples are found to be identical.

**Detailed Logic:**  
- The method first retrieves the samples from the internal state of the `TTestInput` instance.
- It then checks the uniqueness of the samples by converting them into a set, which inherently removes duplicates.
- If the length of the set of samples is less than two, indicating that all samples are identical, the method raises an exception to signal that the input is invalid for statistical testing.
- This validation step is critical to ensure that the subsequent statistical analysis can be performed meaningfully, as identical samples would not provide any information about variability or differences.
```