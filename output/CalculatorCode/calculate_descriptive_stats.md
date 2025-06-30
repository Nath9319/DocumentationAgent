# Documentation for `calculate_descriptive_stats`

```python
def calculate_descriptive_stats(self, series: pd.Series) -> Dict[str, Any]:
    """
    Calculates descriptive statistics for a pandas Series.

    This function computes a variety of descriptive statistics for the 
    provided pandas Series, including count, mean, standard deviation, 
    minimum, maximum, quartiles, median, variance, skewness, and kurtosis. 
    The function ensures that the input series is numeric and raises an 
    error if it is not.

    Parameters:
    ----------
    series : pd.Series
        A pandas Series containing numeric data for which descriptive 
        statistics are to be calculated.

    Returns:
    -------
    Dict[str, Any]
        A dictionary containing the calculated descriptive statistics. 
        The keys include:
        - 'count': Number of non-null entries
        - 'mean': Mean of the series
        - 'std': Standard deviation of the series
        - 'min': Minimum value in the series
        - '25%': 25th percentile (first quartile)
        - '50%': Median (second quartile)
        - '75%': 75th percentile (third quartile)
        - 'max': Maximum value in the series
        - 'median': Median of the series
        - 'variance': Variance of the series
        - 'skewness': Skewness of the series
        - 'kurtosis': Kurtosis of the series

    Raises:
    ------
    DataError
        If the input series is not numeric.

    Notes:
    -----
    The function converts all calculated statistics to float, replacing 
    any NaN values with None for better readability in the output.
    """
    if not pd.api.types.is_numeric_dtype(series):
        raise DataError("Data series must be numeric for statistics.")
    
    stats_dict = series.describe().to_dict()
    stats_dict['median'] = series.median()
    stats_dict['variance'] = series.var()
    stats_dict['skewness'] = series.skew()
    stats_dict['kurtosis'] = series.kurt()
    
    for key, value in stats_dict.items():
        stats_dict[key] = float(value) if pd.notna(value) else None
            
    return stats_dict
```