# Documentation for `StatsService.calculate_z_scores`

```markdown
### calculate_z_scores(numbers: List[float]) -> List[float]

**Description:**  
Calculates the Z-Scores for a given list of numbers. Z-Scores indicate how many standard deviations an element is from the mean of the dataset, providing a way to understand the relative position of each number within the distribution.

**Parameters:**
- `numbers` (`List[float]`): A list of numerical values for which the Z-Scores are to be calculated.

**Expected Input:**  
- `numbers` should be a non-empty list of floats or integers. The list must contain at least one number to compute the mean and standard deviation. If the list is empty, the function may raise an error or return an empty list.

**Returns:**  
`List[float]`: A list of Z-Scores corresponding to the input numbers. Each Z-Score represents the number of standard deviations a number is from the mean of the input list.

**Detailed Logic:**  
- The function first computes the mean of the input list of numbers.
- It then calculates the standard deviation of the same list.
- For each number in the list, the Z-Score is computed using the formula: \( Z = \frac{(X - \text{mean})}{\text{std\_dev}} \), where \( X \) is the number being evaluated.
- The resulting Z-Scores are collected into a new list and returned.
- This function does not rely on any external modules and performs calculations using basic arithmetic operations.
```