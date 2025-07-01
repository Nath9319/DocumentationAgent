# Documentation for `get_correlation_matrix`

```markdown
### get_correlation_matrix(data: pd.DataFrame) -> pd.DataFrame

**Description:**  
The `get_correlation_matrix` function computes the correlation matrix for a given dataset, represented as a Pandas DataFrame. This matrix quantifies the degree to which different variables in the dataset are related to one another, providing insights into potential relationships and dependencies.

**Parameters:**
- `data` (`pd.DataFrame`): A Pandas DataFrame containing the dataset for which the correlation matrix is to be calculated.

**Expected Input:**  
- `data` should be a Pandas DataFrame with numerical columns. The DataFrame can contain any number of rows and columns, but it is expected that the columns represent different variables for which correlations are to be assessed. Non-numeric columns will be ignored in the correlation calculation.

**Returns:**  
`pd.DataFrame`: A DataFrame representing the correlation matrix, where each entry (i, j) indicates the correlation coefficient between the i-th and j-th variables in the input DataFrame.

**Detailed Logic:**  
- The function begins by validating the input to ensure that it is a Pandas DataFrame.
- It then utilizes the `corr()` method provided by Pandas to compute the correlation coefficients between the numerical columns of the DataFrame.
- The resulting correlation matrix is returned as a new DataFrame, which can be further analyzed or visualized by the caller.
- If the input DataFrame is empty or contains no numeric columns, the function may raise an `APIException` to signal an error in processing, ensuring that users receive clear feedback about the nature of the issue.
```