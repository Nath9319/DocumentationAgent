# Documentation for `get_z_scores`

### get_z_scores() -> List[float]

**Description:**
The `get_z_scores` function is designed to handle HTTP POST requests for calculating z-scores from a provided dataset. It serves as an endpoint in a web API, allowing clients to submit numerical data and receive the corresponding z-scores in response. This function leverages dependency injection to access the necessary services and handles potential exceptions that may arise during the calculation process.

**Parameters:**
- `data` (`List[float]`): A list of numerical values for which the z-scores will be calculated. This parameter is expected to be provided in the body of the POST request.

**Expected Input:**
- The `data` parameter should be a non-empty list of floats or integers, representing the dataset for which z-scores are to be computed. The values can include both positive and negative numbers. The function assumes that the list contains at least two elements to compute a meaningful mean and standard deviation.

**Returns:**
`List[float]`: A list of z-scores corresponding to each value in the input dataset. If an error occurs during processing, an appropriate exception is raised.

**Detailed Logic:**
- The function begins by defining an endpoint using the `router.post` decorator, which registers the function to handle incoming POST requests at a specified path.
- It utilizes the `Depends` function to inject the necessary service for calculating z-scores, specifically the `stats_svc.calculate_z_scores` method.
- Upon receiving a request, the function extracts the `data` from the request body and validates it to ensure it meets the expected format.
- It then calls the `calculate_z_scores` method, passing the validated `data` to compute the z-scores.
- If the calculation is successful, the resulting z-scores are returned as a JSON response. If any errors occur during this process, such as invalid input or calculation errors, the function raises an `APIException`, which is handled to return a structured error response to the client.
- This function effectively integrates with the web framework's routing and dependency injection mechanisms, ensuring a clean and maintainable code structure while providing essential statistical functionality.

---
*Generated with 100% context confidence*
