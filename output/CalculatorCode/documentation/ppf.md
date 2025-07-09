# Documentation for `ppf`

### ppf

**Description:**
The `ppf` function computes the percent point function (inverse of the cumulative distribution function) for a specified probability distribution. It is commonly used in statistics to determine the value below which a given percentage of observations fall, effectively allowing users to find critical values associated with specific probabilities.

**Parameters:**
- `q` (`float`): A float value representing the probability for which the percent point function is to be calculated. This value should be in the range [0, 1].
- `dist` (`Distribution`): An instance of a probability distribution class that defines the distribution for which the percent point function is being calculated. This could be any distribution that supports the percent point function.

**Expected Input:**
- `q` must be a float between 0 and 1, inclusive. Values outside this range will result in an error, as they do not correspond to valid probabilities.
- `dist` should be a valid distribution object that implements the necessary methods to compute the percent point function. This typically includes distributions from libraries such as SciPy or similar.

**Returns:**
`float`: The value corresponding to the specified probability `q` for the given distribution. This value indicates the threshold below which the specified percentage of the distribution's values fall.

**Detailed Logic:**
- The function first validates the input probability `q` to ensure it lies within the acceptable range of [0, 1]. If `q` is outside this range, an error is raised.
- It then calls the appropriate method from the `dist` object to compute the percent point function. This method utilizes the underlying mathematical properties of the specified distribution to derive the result.
- The output is a float that represents the critical value for the given probability, which can be used in various statistical analyses, such as hypothesis testing or confidence interval estimation.
- The function does not have any internal dependencies and relies solely on the provided distribution instance to perform its calculations.

---
*Generated with 100% context confidence*
