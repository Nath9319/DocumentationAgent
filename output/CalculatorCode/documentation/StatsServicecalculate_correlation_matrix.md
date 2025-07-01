# Documentation for `StatsService.calculate_correlation_matrix`

### StatsService.calculate_correlation_matrix(columns: List[str]) -> Dict[str, Dict[str, float]]

**Description:**
Calculates the Pearson correlation matrix for the specified columns in the dataset. This method analyzes the linear relationship between pairs of variables, providing insights into how changes in one variable may be associated with changes in another.

**Parameters:**
- `columns` (`List[str]`): A list of strings representing the names of the columns for which the correlation matrix will be calculated.

**Expected Input:**
- `columns` should be a list of valid column names present in the dataset loaded by the service. The dataset must contain numerical data in these columns to compute the correlation accurately. If any column names are invalid or not present in the dataset, the method may raise an error.

**Returns:**
`Dict[str, Dict[str, float]]`: A nested dictionary representing the Pearson correlation coefficients between the specified columns. The outer dictionary's keys are the column names, and each value is another dictionary where the keys are the column names and the values are the correlation coefficients.

**Detailed Logic:**
- The method begins by invoking `self._load_data`, which loads the dataset into a DataFrame. This step is crucial as it ensures that the data is available for analysis.
- It then utilizes the `df.corr()` function from the pandas library to compute the correlation matrix for the specified columns. This function calculates the Pearson correlation coefficients, which measure the linear correlation between pairs of columns.
- Finally, the resulting correlation matrix is converted to a dictionary format using the `to_dict()` method, making it easier to access and interpret the correlation values. The output structure allows for quick lookups of correlation coefficients between any two specified columns.