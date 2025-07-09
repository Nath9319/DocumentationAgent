# Documentation for `df.select_dtypes`

### df.select_dtypes(include=None, exclude=None)

**Description:**
The `select_dtypes` function is a method of a DataFrame that allows users to filter columns based on their data types. This function is particularly useful for selecting specific types of data (e.g., numeric, object, boolean) from a DataFrame, enabling more targeted data manipulation and analysis.

**Parameters:**
- `include` (`str`, `list`, or `None`): Specifies the data types to include in the selection. This can be a single data type (e.g., 'number', 'object') or a list of data types. If set to `None`, all data types are included by default.
- `exclude` (`str`, `list`, or `None`): Specifies the data types to exclude from the selection. Similar to `include`, this can be a single data type or a list. If set to `None`, no data types are excluded.

**Expected Input:**
- The `include` and `exclude` parameters should be strings or lists of strings representing valid data types recognized by the DataFrame (e.g., 'int', 'float', 'object', 'bool'). If both parameters are set to `None`, the function will return all columns.

**Returns:**
`DataFrame`: A new DataFrame containing only the columns that match the specified data types based on the `include` and `exclude` parameters.

**Detailed Logic:**
- The function begins by evaluating the `include` and `exclude` parameters to determine which data types to filter.
- It constructs a mask that identifies columns in the DataFrame that match the specified criteria.
- The function then applies this mask to the DataFrame, returning a new DataFrame that contains only the selected columns.
- If no columns match the criteria, an empty DataFrame is returned.
- This method does not modify the original DataFrame and is designed to provide a view of the data based on type filtering.

---
*Generated with 100% context confidence*
