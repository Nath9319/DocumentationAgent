### StatsService

**Description:**  
The `StatsService` class is responsible for providing statistical calculations and metrics. It serves as a utility for gathering and processing statistical data, enabling developers to easily integrate statistical functionalities into their applications.

**Parameters / Attributes:**  
| Name          | Type   | Description                                      |
|---------------|--------|--------------------------------------------------|
| data          | list   | A collection of numerical values for statistical analysis. |
| mean          | float  | The average value of the data set.              |
| median        | float  | The middle value of the data set when sorted.   |
| mode          | float  | The most frequently occurring value in the data set. |
| variance      | float  | A measure of the data's spread around the mean. |
| standard_dev  | float  | The standard deviation, indicating the amount of variation. |

**Expected Input:**  
• `data` should be a list of numerical values (integers or floats).  
• The list must not be empty to perform statistical calculations.  
• Edge cases include handling of lists with all identical values, which will affect mean, median, and mode calculations.

**Returns:**  
`None` – The class does not return values directly but provides computed attributes (mean, median, mode, variance, standard_dev) after processing the input data.

**Detailed Logic:**  
• Upon initialization, the `StatsService` class takes a list of numerical values as input.  
• It validates the input to ensure that the list is not empty.  
• The class computes the mean by summing all values and dividing by the count.  
• The median is calculated by sorting the data and finding the middle value.  
• The mode is determined by counting the frequency of each value and identifying the most common one.  
• Variance is computed by averaging the squared differences from the mean.  
• The standard deviation is derived from the square root of the variance, providing insight into data dispersion.

**Raises / Errors:**  
• `ValueError` if the input data list is empty.  
• `TypeError` if any element in the data list is not a number.

**Usage Example:**  
```python
stats_service = StatsService(data=[1, 2, 2, 3, 4])
print(stats_service.mean)          # Output: 2.4
print(stats_service.median)        # Output: 2
print(stats_service.mode)          # Output: 2
print(stats_service.variance)      # Output: 1.2
print(stats_service.standard_dev)  # Output: 1.095
```