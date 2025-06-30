# Documentation for `perform_independent_ttest`

```python
def perform_independent_ttest(self, sample1: List[float], sample2: List[float]) -> Dict[str, float]:
    """
    Performs an independent two-sample t-test.

    This function calculates the t-statistic and p-value for two independent samples 
    using the Welch's t-test, which does not assume equal population variance.

    Parameters:
    ----------
    sample1 : List[float]
        The first sample of data points.
    sample2 : List[float]
        The second sample of data points.

    Returns:
    -------
    Dict[str, float]
        A dictionary containing the following keys:
        - "t_statistic": The calculated t-statistic for the test.
        - "p_value": The p-value associated with the t-statistic.
    
    Example:
    --------
    >>> result = perform_independent_ttest([1.2, 2.3, 3.1], [2.1, 3.4, 4.2])
    >>> print(result)
    {'t_statistic': -1.234, 'p_value': 0.234}
    """
    ttest_result = stats.ttest_ind(sample1, sample2, equal_var=False)
    return {
        "t_statistic": float(ttest_result.statistic),
        "p_value": float(ttest_result.pvalue)
    }
``` 

### Explanation of the Documentation:
- **Function Purpose:** The docstring begins with a clear statement of the function's purpose, specifying that it performs an independent two-sample t-test.
- **Detailed Description:** It includes a brief explanation of the statistical method used (Welch's t-test) and its assumption regarding population variance.
- **Parameters Section:** Each parameter is described, including its type and purpose.
- **Returns Section:** The return type is specified, along with a description of the contents of the returned dictionary.
- **Example Usage:** An example of how to call the function and what the output looks like is provided, enhancing usability for future developers.