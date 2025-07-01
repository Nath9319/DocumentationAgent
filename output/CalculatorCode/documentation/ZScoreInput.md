# Documentation for `ZScoreInput`

### ZScoreInput

**Description:**
`ZScoreInput` is a class designed to facilitate the calculation of Z-scores, which are statistical measures that describe a value's relation to the mean of a group of values. This class likely extends the functionality of a base model, providing a structured way to handle input data necessary for Z-score calculations.

**Parameters/Attributes:**
- **Attributes:**
  - `data` (`List[float]`): A list of numerical values for which the Z-scores will be calculated. This attribute is essential for the class's functionality.
  
**Expected Input:**
- The `data` attribute should be a list of floats, where each float represents a numerical value. The list should not be empty, as Z-scores require a mean and standard deviation to be calculated.

**Returns:**
`None`: The class does not return a value directly. Instead, it is expected to provide methods for calculating and retrieving Z-scores based on the input data.

**Detailed Logic:**
- The `ZScoreInput` class inherits from `BaseModel`, which suggests that it may utilize or override methods and properties defined in the base class.
- The class is likely designed to process the input data, calculating the mean and standard deviation as part of the Z-score computation.
- It may include methods for validating the input data, ensuring that it meets the necessary criteria for statistical analysis.
- The class does not directly interact with external libraries or modules, but it relies on built-in Python types and functionalities to manage and manipulate the input data.