# Documentation for `StatsService.calculate_correlation_matrix`

```python
def calculate_correlation_matrix(self, db_path, table_name, columns):
    """
    Calculate the Pearson correlation matrix for specified columns in a database table.

    This method retrieves data from the specified database and table, then computes
    the Pearson correlation coefficients for the given columns. The resulting 
    correlation matrix is returned as a dictionary.

    Parameters:
    ----------
    db_path : str
        The file path to the database from which to load the data.
    table_name : str
        The name of the table containing the data.
    columns : list of str
        A list of column names for which to calculate the correlation matrix.

    Returns:
    -------
    dict
        A dictionary representation of the Pearson correlation matrix, where
        keys are column names and values are dictionaries of correlation coefficients
        with respect to other columns.

    Example:
    --------
    >>> correlation_matrix = stats_service.calculate_correlation_matrix('path/to/db.sqlite', 'my_table', ['col1', 'col2', 'col3'])
    >>> print(correlation_matrix)
    {'col1': {'col1': 1.0, 'col2': 0.8, 'col3': -0.5}, 
     'col2': {'col1': 0.8, 'col2': 1.0, 'col3': 0.1}, 
     'col3': {'col1': -0.5, 'col2': 0.1, 'col3': 1.0}}
    """
    df = self._load_data(db_path, table_name, columns)
    corr_matrix = df.corr(method='pearson').to_dict()
    return corr_matrix
``` 

### Documentation Breakdown:
- **Purpose:** Clearly states what the method does, including the type of correlation calculated (Pearson).
- **Parameters:** Describes each parameter, including its type and purpose.
- **Returns:** Specifies the return type and structure of the output.
- **Example:** Provides a practical example of how to use the method, illustrating input and output.