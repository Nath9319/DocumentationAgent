# Documentation for `df.corr`

### df.corr()

**Description:**
The `df.corr()` function computes the pairwise correlation of columns in a DataFrame, excluding NA/null values. It provides a measure of the linear relationship between two variables, which can be useful for understanding the relationships within the data.

**Parameters:**
None.

**Expected Input:**
- The function operates on a DataFrame object, which is expected to contain numerical data. Non-numeric columns will be ignored in the correlation computation.
- The DataFrame may contain missing values (NA/null), which will be excluded from the correlation calculations.

**Returns:**
`DataFrame`: A DataFrame containing the correlation coefficients between the columns of the input DataFrame. The resulting DataFrame is symmetric, with the correlation of each column with itself being 1.

**Detailed Logic:**
- The function begins by identifying all numeric columns in the DataFrame.
- It then computes the correlation matrix using a specified method (default is Pearson correlation), which measures the linear correlation between pairs of columns.
- The correlation coefficients are calculated by evaluating the covariance of the columns relative to their standard deviations.
- The resulting correlation matrix is returned as a new DataFrame, where the index and columns correspond to the original DataFrame's columns, allowing for easy interpretation of the relationships between variables.
- The function does not rely on any external dependencies, ensuring that it operates solely within the context of the DataFrame provided.

---
*Generated with 100% context confidence*
