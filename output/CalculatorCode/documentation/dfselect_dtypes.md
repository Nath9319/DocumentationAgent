# Documentation for `df.select_dtypes`

### df.select_dtypes

**Description:**
The `select_dtypes` function is a method of a DataFrame object that allows users to filter columns based on their data types. This function is particularly useful for data manipulation and analysis, enabling users to easily select columns of specific types (e.g., numeric, object, boolean) for further processing or analysis.

**Parameters:**
- `include` (`str` or list of str, optional): Specifies the data types to include in the selection. This can be a single data type (e.g., 'number') or a list of types (e.g., ['float64', 'int64']).
- `exclude` (`str` or list of str, optional): Specifies the data types to exclude from the selection. Similar to `include`, this can be a single type or a list of types.

**Expected Input:**
- The `include` and `exclude` parameters should be strings or lists of strings representing valid data types recognized by the DataFrame. Common types include:
  - 'number': for all numeric types (integers and floats)
  - 'object': for string or mixed types
  - 'bool': for boolean types
  - Specific types like 'int64', 'float64', etc.
- If both `include` and `exclude` are provided, the function will first filter based on `include` and then remove any columns that match the `exclude` criteria.

**Returns:**
`DataFrame`: A new DataFrame containing only the columns that match the specified data types as defined by the `include` and `exclude` parameters.

**Detailed Logic:**
- The function begins by validating the `include` and `exclude` parameters to ensure they are of the correct type (string or list of strings).
- It then retrieves the data types of all columns in the DataFrame.
- Based on the `include` parameter, it identifies which columns match the specified types and creates a subset of the DataFrame.
- Next, if the `exclude` parameter is provided, it further filters out any columns that match the excluded types from the previously created subset.
- The final result is a DataFrame that contains only the columns of the specified types, allowing for streamlined data analysis and manipulation. This method does not rely on any external modules and operates solely on the DataFrame's internal structure.

---
*Generated with 100% context confidence*
