# Documentation for `get_descriptive_stats`

### get_descriptive_stats() -> dict

**Description:**
The `get_descriptive_stats` function is designed to handle HTTP POST requests for calculating and returning descriptive statistics of a provided dataset. It serves as an endpoint in a web API, allowing clients to submit data and receive a summary of key statistical measures, such as mean, median, mode, standard deviation, and range.

**Parameters:**
- `data` (`List[float]`): A list of numerical values representing the dataset for which descriptive statistics are to be calculated. This parameter is typically extracted from the request body of the POST request.

**Expected Input:**
- The `data` parameter should be a non-empty list containing numerical values (either integers or floats). The dataset must not contain any non-numeric types or be empty, as this would lead to errors in statistical calculations. Special cases, such as handling missing values or outliers, should be considered in the dataset.

**Returns:**
`dict`: A dictionary containing the calculated descriptive statistics, which may include:
- `mean`: The average value of the dataset.
- `median`: The middle value when the dataset is sorted.
- `mode`: The most frequently occurring value(s) in the dataset.
- `std_dev`: The standard deviation, indicating the amount of variation or dispersion in the dataset.
- `range`: The difference between the maximum and minimum values in the dataset.

**Detailed Logic:**
- The function begins by validating the input data to ensure it is a non-empty list of numerical values.
- It utilizes the `calculate_descriptive_stats` function from the `stats_svc` service to compute the descriptive statistics for the provided dataset.
- Upon successful calculation, the resulting statistics are formatted into a dictionary and returned as the response to the client.
- If any errors occur during processing (e.g., invalid input data), the function raises an `APIException`, which is handled by the application's error management system to provide a structured JSON error response.
- This function is registered as a POST endpoint using the `router.post` method, allowing it to respond to incoming requests at the specified API route.

---
*Generated with 100% context confidence*
