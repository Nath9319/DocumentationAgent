# Documentation for `TTestInput`

```python
class TTestInput(BaseModel):
    """
    Model for an independent t-test. Validates that samples are not identical.

    This class represents the input required for performing an independent t-test.
    It ensures that the two samples provided are not identical, which is a prerequisite
    for conducting a valid t-test.

    Attributes:
        sample1 (List[float]): The first sample for the t-test. Must contain at least 
                                two elements.
        sample2 (List[float]): The second sample for the t-test. Must contain at least 
                                two elements.

    Validation:
        The `samples_must_not_be_identical` method is used to validate that `sample2` 
        is not identical to `sample1`. If they are the same, a ValueError is raised.

    Example:
        >>> t_test_input = TTestInput(sample1=[1.0, 2.0], sample2=[3.0, 4.0])
        >>> t_test_input = TTestInput(sample1=[1.0, 2.0], sample2=[1.0, 2.0])
        ValueError: Sample 1 and Sample 2 cannot be identical for a t-test.
    """
    sample1: List[float] = Field(..., min_length=2)
    sample2: List[float] = Field(..., min_length=2)

    @field_validator('sample2')
    @classmethod
    def samples_must_not_be_identical(cls, v, values):
        if 'sample1' in values.data and v == values.data['sample1']:
            raise ValueError('Sample 1 and Sample 2 cannot be identical for a t-test.')
        return v
``` 

### Documentation Breakdown:

- **Class Purpose**: Clearly states that the class is for modeling input for an independent t-test and highlights the validation requirement.
- **Attributes**: Describes the attributes `sample1` and `sample2`, including their types and constraints (minimum length).
- **Validation Logic**: Summarizes the validation method and its purpose.
- **Example Usage**: Provides a practical example of how to instantiate the class and the expected behavior when samples are identical, enhancing user understanding.