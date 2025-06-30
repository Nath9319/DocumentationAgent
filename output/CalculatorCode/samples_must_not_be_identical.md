# Documentation for `samples_must_not_be_identical`

```python
def samples_must_not_be_identical(cls, v, values):
    """
    Validate that two samples are not identical.

    This method is automatically invoked during the validation process. It checks
    whether the provided sample (sample2) is identical to sample1. If they are
    the same, a ValueError is raised, indicating that the two samples cannot
    be identical for a t-test.

    Parameters:
    cls: The class that this method belongs to.
    v: The value of sample2 being validated.
    values: An object containing the data of the samples being compared.
            It must have a 'data' attribute that includes 'sample1'.

    Raises:
    ValueError: If sample2 (v) is identical to sample1.

    Returns:
    The validated value (v) if the samples are not identical.
    """
    if 'sample1' in values.data and v == values.data['sample1']:
        raise ValueError("Sample 1 and Sample 2 cannot be identical for a t-test.")
    return v
``` 

### Summary of Changes:
- Expanded the existing docstring to provide a clear description of the function's purpose, parameters, exceptions raised, and return value.
- Ensured the documentation adheres to standard conventions for clarity and usability.