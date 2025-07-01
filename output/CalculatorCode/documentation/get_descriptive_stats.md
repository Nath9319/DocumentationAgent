# Documentation for `get_descriptive_stats`

```markdown
### get_descriptive_stats(data: list) -> dict

**Description:**  
The `get_descriptive_stats` function computes and returns a set of descriptive statistics for a given dataset. This includes key metrics such as mean, median, standard deviation, minimum, and maximum values, providing a comprehensive overview of the data's distribution and central tendency.

**Parameters:**
- `data` (`list`): A list of numerical values for which the descriptive statistics are to be calculated.

**Expected Input:**  
- `data` should be a list containing numerical values (integers or floats). The list must not be empty, as descriptive statistics cannot be computed on an empty dataset. If the list contains non-numeric values, an exception will be raised.

**Returns:**  
`dict`: A dictionary containing the calculated descriptive statistics, including:
  - `mean`: The average of the data points.
  - `median`: The middle value when the data points are sorted.
  - `std_dev`: The standard deviation, indicating the dispersion of the data points.
  - `min`: The smallest value in the dataset.
  - `max`: The largest value in the dataset.

**Detailed Logic:**  
- The function begins by validating the input to ensure that the `data` list is not empty and contains only numeric values.
- It then calculates the mean by summing all the values and dividing by the count of values.
- The median is computed by sorting the data and finding the middle value, taking care to handle both even and odd lengths of the list appropriately.
- The standard deviation is calculated using the formula that measures the amount of variation or dispersion of the dataset.
- Finally, the function identifies the minimum and maximum values in the dataset.
- If any errors occur during these calculations, such as invalid input types or empty datasets, the function raises an `APIException` with an appropriate message and status code, ensuring that error handling is consistent with the API's design.
```