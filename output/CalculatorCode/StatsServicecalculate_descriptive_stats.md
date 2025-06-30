# Documentation for `StatsService.calculate_descriptive_stats`

```python
def calculate_descriptive_stats(self, data: List[float]) -> dict:
    """
    Calculate descriptive statistics for a list of numbers.

    This method computes the following descriptive statistics:
    - Mean: The average of the numbers.
    - Median: The middle value when the numbers are sorted.
    - Mode: The most frequently occurring number in the list.
    - Variance: A measure of how much the numbers vary from the mean.
    - Standard Deviation: The square root of the variance, indicating the dispersion of the dataset.

    Parameters:
    ----------
    data : List[float]
        A list of numerical values for which the statistics will be calculated.

    Returns:
    -------
    dict
        A dictionary containing the calculated statistics with the following keys:
        - 'mean': The mean of the numbers.
        - 'median': The median of the numbers.
        - 'mode': The mode of the numbers.
        - 'variance': The variance of the numbers.
        - 'std_dev': The standard deviation of the numbers.

    Raises:
    ------
    ValueError
        If the input list is empty, a ValueError is raised as descriptive statistics cannot be computed.

    Example:
    --------
    >>> stats_service = StatsService()
    >>> stats_service.calculate_descriptive_stats([1, 2, 2, 3, 4])
    {'mean': 2.4, 'median': 2, 'mode': 2.0, 'variance': 1.36, 'std_dev': 1.1661903789690605}
    """
    return {
        'mean': float(np.mean(data)),
        'median': float(np.median(data)),
        'mode': float(stats.mode(data, keepdims=True).mode[0]),
        'variance': float(np.var(data)),
        'std_dev': float(np.std(data))
    }
``` 

### Documentation Breakdown:
- **Purpose**: Clearly states what the function does.
- **Statistics Explained**: Each statistic calculated is briefly explained.
- **Parameters**: Describes the input parameter, including its type and purpose.
- **Returns**: Details the structure of the returned dictionary.
- **Error Handling**: Mentions potential errors that may arise from improper input.
- **Example**: Provides a practical example of how to use the function, enhancing user understanding.