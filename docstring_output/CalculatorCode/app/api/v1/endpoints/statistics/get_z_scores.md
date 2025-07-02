### get_z_scores(data: list) -> list

**Description:**  
Calculates the z-scores for a given list of numerical data, providing a standardized measure of how far each data point is from the mean in terms of standard deviations.

**Parameters:**  
| Name   | Type  | Description                                   |
|--------|-------|-----------------------------------------------|
| data   | list  | A list of numerical values for which z-scores are to be calculated. |

**Expected Input:**  
• `data` must be a non-empty list of numerical values (integers or floats).  
• The list should contain at least two values to compute a meaningful z-score.

**Returns:**  
`list` – A list of z-scores corresponding to each value in the input list.

**Detailed Logic:**  
• Computes the mean of the input data.  
• Calculates the standard deviation of the input data.  
• For each value in the input list, computes the z-score using the formula:  
  \[ z = \frac{(X - \text{mean})}{\text{std\_dev}} \]  
  where \( X \) is the individual data point, `mean` is the average of the data, and `std_dev` is the standard deviation.  
• Returns a list of computed z-scores.

**Raises / Errors:**  
• Raises a `ValueError` if the input list is empty or contains non-numeric values.  
• Raises a `ZeroDivisionError` if the standard deviation is zero (i.e., all values in the list are identical).

**Usage Example:**  
```python
data = [10, 12, 23, 23, 16, 23, 21, 16]
z_scores = get_z_scores(data)
print(z_scores)
```