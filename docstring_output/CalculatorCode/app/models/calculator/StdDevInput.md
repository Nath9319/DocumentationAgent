### StdDevInput

**Description:**  
Model for Standard Deviation calculation.

**Parameters / Attributes:**  
| Name       | Type   | Description                          |
|------------|--------|--------------------------------------|
| data       | list   | A list of numerical values for which the standard deviation is calculated. |

**Expected Input:**  
• `data` must be a list of numbers (integers or floats).  
• The list should contain at least one element.  
• Edge cases include an empty list, which may raise an error.

**Returns:**  
`float` – the calculated standard deviation of the input data.

**Detailed Logic:**  
• The model computes the mean of the input data.  
• It then calculates the squared differences from the mean for each data point.  
• The average of these squared differences is computed.  
• Finally, the square root of this average gives the standard deviation.

**Raises / Errors:**  
• Raises a `ValueError` if the input list is empty.  
• Raises a `TypeError` if any element in the list is not a number.

**Usage Example:**  
```python
std_dev = StdDevInput(data=[10, 12, 23, 23, 16, 23, 21, 16])
print(std_dev)  # Outputs the standard deviation of the provided data.
```