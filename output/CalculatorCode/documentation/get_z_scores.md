# Documentation for `get_z_scores`

### get_z_scores() -> List[float]

**Description:**
The `get_z_scores` function is designed to handle HTTP POST requests for calculating z-scores based on a provided dataset. It processes incoming data, validates it, and utilizes a statistical service to compute the z-scores, which indicate how many standard deviations each element in the dataset is from the mean.

**Parameters:**
- `data` (`List[float]`): A list of numerical values for which the z-scores will be calculated. This parameter is expected to be provided in the body of the POST request.

**Expected Input:**
- The `data` parameter should be a non-empty list of floats or integers. The values can be positive, negative, or zero, but the list must contain at least one element to compute the mean and standard deviation. If the input is invalid or empty, an appropriate error response will be generated.

**Returns:**
`List[float]`: A list of z-scores corresponding to each value in the input dataset. If the input is invalid, the function will raise an `APIException` with an appropriate error message.

**Detailed Logic:**
- The function begins by extracting the `data` from the incoming POST request.
- It validates the input to ensure that it is a non-empty list of numerical values. If the validation fails, it raises an `APIException` to inform the client of the error.
- Upon successful validation, the function calls the `calculate_z_scores` method from the `stats_svc` service, passing the validated data as an argument.
- The `calculate_z_scores` function computes the z-scores for the dataset by first calculating the mean and standard deviation, then applying the z-score formula for each element.
- The resulting list of z-scores is returned as the response to the original POST request, allowing the client to receive the computed statistical data.

---
*Generated with 100% context confidence*
