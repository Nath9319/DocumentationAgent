# Documentation for `df.select_dtypes`

### df.select_dtypes(include=None, exclude=None)

**Description:**
The `select_dtypes` function is a method of the DataFrame object that allows users to filter columns based on their data types. This function is particularly useful for data manipulation and analysis, enabling users to easily select subsets of data that match specific type criteria.

**Parameters:**
- `include` (`str`, `type`, or `list` of `str`/`type`, optional): Specifies the data types to include in the selection. This can be a single data type, a list of data types, or a string that represents a data type (e.g., 'number', 'object', 'datetime').
- `exclude` (`str`, `type`, or `list` of `str`/`type`, optional): Specifies the data types to exclude from the selection. Similar to `include`, this can be a single data type, a list of data types, or a string.

**Expected Input:**
- The `include` and `exclude` parameters can accept various data types, including built-in Python types (like `int`, `float`, `str`) and NumPy data types (like `np.int64`, `np.float64`). Users can also provide strings that represent data types.
- If both `include` and `exclude` are set, the function will prioritize the `include` parameter.

**Returns:**
`DataFrame`: A new DataFrame containing only the columns that match the specified data types in the `include` parameter, while excluding those specified in the `exclude` parameter.

**Detailed Logic:**
- The function begins by validating the input parameters to ensure they are of the correct type and format.
- It then identifies the data types of each column in the DataFrame.
- Based on the `include` and `exclude` parameters, it filters the columns, retaining only those that match the specified criteria.
- The resulting DataFrame is constructed and returned, containing only the selected columns.
- This method does not rely on any external modules and operates solely on the DataFrame's internal structure and metadata.

---
*Generated with 100% context confidence*
