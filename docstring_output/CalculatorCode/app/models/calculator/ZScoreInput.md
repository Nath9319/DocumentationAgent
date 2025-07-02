### ZScoreInput

**Description:**  
Represents an input structure for calculating the Z-score, which is a statistical measurement that describes a value's relation to the mean of a group of values.

**Parameters:**  
| Name      | Type   | Description                                   |
|-----------|--------|-----------------------------------------------|
| value     | float  | The raw score or value for which the Z-score is calculated. |
| mean      | float  | The mean of the dataset from which the Z-score is derived. |
| std_dev   | float  | The standard deviation of the dataset.       |

**Expected Input:**  
• `value` can be any float number.  
• `mean` must be a float representing the average of the dataset.  
• `std_dev` must be a float greater than 0 to avoid division by zero.

**Returns:**  
`float` – the calculated Z-score, which indicates how many standard deviations the `value` is from the `mean`.

**Detailed Logic:**  
• The Z-score is calculated using the formula:  
  \[ Z = \frac{(value - mean)}{std\_dev} \]  
• The input `value` is subtracted from the `mean`, and the result is divided by `std_dev`.  
• This calculation provides a standardized score that can be used to compare values from different datasets.

**Raises / Errors:**  
• Raises a `ValueError` if `std_dev` is zero or negative, as this would lead to an invalid calculation.

**Usage Example:**  
```python
z_score = ZScoreInput(value=10.0, mean=5.0, std_dev=2.0)
print(z_score)  # Output: 2.5
```