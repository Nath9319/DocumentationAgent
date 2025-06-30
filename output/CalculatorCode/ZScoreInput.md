# Documentation for `ZScoreInput`

```python
class ZScoreInput(BaseModel):
    """
    ZScoreInput is a model for Z-Score calculation.

    Attributes:
        data (List[float]): A list of numerical values for which the Z-Score will be calculated.
    """

    data: List[float]
```

### Documentation for `ZScoreInput`

#### Class: `ZScoreInput`

**File Path:** `app/models/calculator.py`  
**Lines:** 130 to 132

**Description:**  
`ZScoreInput` is a data model designed to facilitate the calculation of Z-Scores from a list of numerical values. It inherits from `BaseModel`, ensuring that it follows the structure and validation rules defined in the base class.

**Attributes:**

- `data` (List[float]):  
  A list containing float values. This attribute holds the numerical data for which the Z-Scores will be computed.

**Usage Example:**
```python
z_score_input = ZScoreInput(data=[10.0, 20.0, 30.0])
```

**Notes:**  
- Ensure that the `data` attribute contains valid numerical values to avoid errors during Z-Score calculations.
- This class does not have any internal dependencies, making it lightweight and easy to integrate into other components of the application.