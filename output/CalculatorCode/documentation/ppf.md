# Documentation for `ppf`

### ppf

**Description:**
The `ppf` function computes the inverse of the cumulative distribution function (CDF) for a specified probability distribution. It is commonly used in statistical analysis to determine the value associated with a given percentile in a distribution, allowing users to find the quantile corresponding to a specified probability.

**Parameters:**
- `q` (`float`): A probability value between 0 and 1, representing the quantile to be computed.
- `loc` (`float`, optional): The location parameter of the distribution, which shifts the distribution along the x-axis. Default is 0.
- `scale` (`float`, optional): The scale parameter of the distribution, which stretches or compresses the distribution. Default is 1.

**Expected Input:**
- `q` must be a float in the range [0, 1]. Values outside this range will result in an error.
- `loc` and `scale` should be floats, where `scale` must be a positive value. If `scale` is zero or negative, it will raise an error.

**Returns:**
`float`: The quantile value corresponding to the input probability `q` for the specified distribution parameters.

**Detailed Logic:**
- The function first validates the input probability `q` to ensure it lies within the acceptable range of [0, 1].
- It then applies the inverse CDF formula specific to the distribution defined by the parameters `loc` and `scale`.
- The result is computed based on the distribution's characteristics, which may involve mathematical transformations or lookups.
- The function does not depend on any internal modules, relying solely on its own logic to perform the calculations.

---
*Generated with 100% context confidence*
