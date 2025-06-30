# Documentation for `ConfidenceIntervalInput`

```python
class ConfidenceIntervalInput(BaseModel):
    """
    Model for Confidence Interval calculation.

    Attributes:
        data (List[float]): A list of numerical values for which the confidence interval 
                            will be calculated. This list must contain at least two 
                            elements to compute a valid confidence interval.
        confidence (float): The confidence level for the interval, expressed as a 
                            decimal. The default value is 0.95, representing a 95% 
                            confidence level. This value must be between 0 and 1.
    """
    data: List[float]
    confidence: float = 0.95
```

### Documentation Breakdown:

- **Class Name:** `ConfidenceIntervalInput`
- **Base Class:** Inherits from `BaseModel`, which may provide additional functionality or validation.
- **Purpose:** This class is designed to encapsulate the input parameters required for calculating a confidence interval based on a dataset.
- **Attributes:**
  - `data`: A list of floating-point numbers representing the sample data.
  - `confidence`: A floating-point number indicating the desired confidence level for the interval, with a default of 0.95.

### Usage Notes:
- Ensure that the `data` attribute contains at least two numerical values to perform a valid confidence interval calculation.
- The `confidence` attribute should be set within the range of 0 to 1 to reflect valid confidence levels.