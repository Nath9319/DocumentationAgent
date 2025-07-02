### DescriptiveStatsInput

**Description:**  
Model for Descriptive Statistics calculation, designed to facilitate the computation of various statistical metrics from input data.

**Parameters / Attributes:**  
| Name           | Type   | Description                                      |
|----------------|--------|--------------------------------------------------|
| data           | list   | A collection of numerical values for analysis.   |
| mean           | float  | The average of the input data.                   |
| median         | float  | The middle value of the input data when sorted.  |
| mode           | float  | The most frequently occurring value in the data. |
| variance       | float  | Measure of the data's spread around the mean.    |
| standard_deviation | float | The square root of the variance, indicating spread. |

**Expected Input:**  
• `data` should be a list of numerical values (integers or floats).  
• The list must not be empty.  
• Edge cases include handling of lists with all identical values (leading to variance and standard deviation of zero).

**Returns:**  
An instance of `DescriptiveStatsInput` containing computed statistical metrics (mean, median, mode, variance, standard deviation).

**Detailed Logic:**  
• Upon initialization, the model computes the mean by summing all values and dividing by the count.  
• The median is determined by sorting the data and finding the middle value.  
• Mode is calculated by counting occurrences of each value and identifying the most frequent.  
• Variance is computed as the average of the squared differences from the mean.  
• Standard deviation is derived from the variance by taking its square root.  
• The model may interact with other components for data validation or additional statistical calculations.

**Raises / Errors:**  
• Raises `ValueError` if the input data is empty.  
• May raise `TypeError` if non-numeric values are included in the data list.

**Usage Example:**  
```python
stats = DescriptiveStatsInput(data=[1, 2, 2, 3, 4])
print(stats.mean)  # Output: 2.4
print(stats.median)  # Output: 2
print(stats.mode)  # Output: 2
print(stats.variance)  # Output: 1.2
print(stats.standard_deviation)  # Output: 1.0954451150103321
```