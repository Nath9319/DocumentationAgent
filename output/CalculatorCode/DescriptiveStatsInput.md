# Documentation for `DescriptiveStatsInput`

```python
class DescriptiveStatsInput(BaseModel):
    """
    Model for Descriptive Statistics calculation.

    This class serves as a data model for input required to perform
    descriptive statistics calculations. It inherits from BaseModel
    and contains a single attribute:

    Attributes:
        data (List[float]): A list of numerical values for which
        descriptive statistics will be computed. This list must
        contain float values.

    Example:
        >>> stats_input = DescriptiveStatsInput(data=[1.0, 2.5, 3.3])
        >>> print(stats_input.data)
        [1.0, 2.5, 3.3]
    """
    data: List[float]
```

### Documentation Breakdown:
- **Class Purpose:** The docstring clearly states that the class is a model for descriptive statistics calculations.
- **Attributes Section:** It describes the `data` attribute, specifying its type and purpose.
- **Example Usage:** An example is provided to illustrate how to instantiate the class and access its attribute, enhancing clarity for users.