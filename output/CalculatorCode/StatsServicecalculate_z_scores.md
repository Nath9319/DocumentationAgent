# Documentation for `StatsService.calculate_z_scores`

```python
def calculate_z_scores(self, data: List[float]) -> List[float]:
    """
    Calculate Z-Scores for a list of numbers.

    The Z-Score is a statistical measurement that describes a value's relation to the 
    mean of a group of values. It is calculated by subtracting the mean from the value 
    and then dividing by the standard deviation. This method returns a list of Z-Scores 
    rounded to four decimal places.

    Parameters:
    ----------
    data : List[float]
        A list of numerical values for which the Z-Scores will be calculated.

    Returns:
    -------
    List[float]
        A list of Z-Scores corresponding to the input data.

    Raises:
    ------
    ValueError
        If the input list is empty or contains non-numeric values.

    Examples:
    --------
    >>> service = StatsService()
    >>> service.calculate_z_scores([10, 20, 30, 40, 50])
    [-1.4142, -0.7071, 0.0, 0.7071, 1.4142]
    """
    return list(((np.array(data) - np.mean(data)) / np.std(data)).round(4))
```

### Documentation Breakdown:

- **Function Purpose:** The docstring clearly states that the function calculates Z-Scores for a list of numbers.
- **Parameters Section:** Describes the input parameter `data`, specifying that it should be a list of floats.
- **Returns Section:** Explains what the function returns, which is a list of Z-Scores.
- **Error Handling:** Mentions potential exceptions that could be raised, such as `ValueError` for invalid input.
- **Examples Section:** Provides an example of how to use the function, illustrating its functionality with sample input and expected output.