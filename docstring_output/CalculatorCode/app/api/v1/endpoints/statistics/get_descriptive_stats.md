### get_descriptive_stats(data: list) -> dict

**Description:**  
Calculates descriptive statistics for a given dataset, providing insights such as mean, median, mode, standard deviation, and variance.

**Parameters:**  
| Name   | Type  | Description                                |
|--------|-------|--------------------------------------------|
| data   | list  | A list of numerical values for analysis.   |

**Expected Input:**  
• `data` must be a list of numbers (integers or floats).  
• The list should not be empty.  
• All elements in the list should be of numeric type.

**Returns:**  
`dict` – A dictionary containing the calculated descriptive statistics, including mean, median, mode, standard deviation, and variance.

**Detailed Logic:**  
• Validates that the input `data` is a non-empty list of numbers.  
• Computes the mean by summing all elements and dividing by the count.  
• Determines the median by sorting the list and finding the middle value(s).  
• Calculates the mode by identifying the most frequently occurring value(s).  
• Computes the standard deviation and variance using the appropriate statistical formulas.  
• Returns a dictionary with all computed statistics for easy access.

