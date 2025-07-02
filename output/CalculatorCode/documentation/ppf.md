# Documentation for `ppf`

### ppf

**Description:**
The `ppf` function computes the percent point function (inverse of the cumulative distribution function) for a specified probability distribution. It is commonly used in statistical analysis to determine the value below which a given percentage of observations fall, effectively allowing users to find critical values associated with various statistical distributions.

**Parameters:**
- `q` (`float`): A float representing the quantile or probability value, which must be between 0 and 1 (exclusive). This indicates the probability threshold for which the corresponding value is sought.
- `loc` (`float`, optional): A float representing the location parameter of the distribution. This parameter shifts the distribution along the x-axis.
- `scale` (`float`, optional): A float representing the scale parameter of the distribution. This parameter stretches or compresses the distribution along the x-axis.

**Expected Input:**
- `q` must be a float in the range (0, 1). Values outside this range will result in an error.
- `loc` and `scale` are optional parameters. If provided, `scale` must be a positive float, while `loc` can be any float.

**Returns:**
`float`: The value corresponding to the specified quantile for the distribution defined by the `loc` and `scale` parameters.

**Detailed Logic:**
- The function first validates the input probability `q` to ensure it falls within the acceptable range (0, 1). If `q` is outside this range, an error is raised.
- If the `scale` parameter is provided, it is checked to ensure it is a positive value, as a non-positive scale does not make sense in the context of probability distributions.
- The function then applies the appropriate mathematical transformations based on the specified distribution type to compute the quantile value. This typically involves using the cumulative distribution function (CDF) and its inverse.
- The result is adjusted according to the `loc` and `scale` parameters, allowing for flexibility in the distribution's positioning and spread.
- The function does not rely on any internal dependencies, making it a standalone utility for statistical calculations.

---
*Generated with 100% context confidence*
