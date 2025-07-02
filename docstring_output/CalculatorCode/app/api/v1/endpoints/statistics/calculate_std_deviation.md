### calculate_std_deviation(data: List[float]) -> float

**Description:**  
Calculates the standard deviation of a given dataset, providing a measure of the amount of variation or dispersion in the dataset.

**Parameters:**  
| Name  | Type          | Description                               |
|-------|---------------|-------------------------------------------|
| data  | List[float]   | A list of numerical values for which the standard deviation is to be calculated. |

**Expected Input:**  
• `data` must be a non-empty list of numerical values (floats or integers).  
• The list should contain at least two elements to compute a meaningful standard deviation.

**Returns:**  
`float` – the standard deviation of the input dataset, representing the average distance of each data point from the mean.

**Detailed Logic:**  
• First, compute the mean (average) of the dataset.  
• Then, calculate the squared differences between each data point and the mean.  
• Sum these squared differences.  
• Divide the sum by the number of data points minus one (for sample standard deviation).  
• Finally, take the square root of the result to obtain the standard deviation.

**Raises / Errors:**  
• Raises a `ValueError` if the input list `data` is empty or contains fewer than two elements.

**Usage Example:**  
```python
data = [10, 12, 23, 23, 16, 23, 21, 16]
std_dev = calculate_std_deviation(data)
print(std_dev)  # Output: Standard deviation of the dataset
```