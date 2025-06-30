# Documentation for `get_descriptive_stats`

```python
def get_descriptive_stats(payload: DescriptiveStatsInput, stats_svc: StatsService=Depends(lambda: stats_service)):
    """
    Calculate descriptive statistics based on the provided input data.

    This function is an endpoint that receives a payload containing data for which 
    descriptive statistics are to be calculated. It utilizes the `StatsService` 
    to perform the calculations and returns the results in a structured format.

    Parameters:
    ----------
    payload : DescriptiveStatsInput
        An object containing the input data for which descriptive statistics 
        are to be calculated. This should conform to the expected structure 
        defined in the `DescriptiveStatsInput` class.

    stats_svc : StatsService, optional
        An instance of the `StatsService` class, which provides the method 
        to calculate descriptive statistics. This is injected using FastAPI's 
        dependency injection system.

    Returns:
    -------
    dict
        A dictionary containing the analysis type and the calculated results. 
        The structure of the returned dictionary is as follows:
        - 'analysis_type': A string indicating the type of analysis performed.
        - 'results': The calculated descriptive statistics.

    Raises:
    ------
    APIException
        If an error occurs during the calculation of descriptive statistics, 
        an `APIException` is raised with a status code of 400 and a detail 
        message describing the error.

    Example:
    --------
    To call this endpoint, send a POST request to `/descriptive_stats` 
    with a JSON body that matches the `DescriptiveStatsInput` schema. 
    The response will include the analysis type and the results of the 
    descriptive statistics calculation.

    """
    try:
        result = stats_svc.calculate_descriptive_stats(payload.data)
        return {'analysis_type': 'Descriptive Statistics', 'results': result}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
``` 

### Documentation Overview:
- **Function Purpose:** The `get_descriptive_stats` function serves as an API endpoint for calculating descriptive statistics based on input data.
- **Parameters:** It takes a `DescriptiveStatsInput` object and an optional `StatsService` instance.
- **Returns:** A dictionary with the analysis type and results.
- **Error Handling:** It raises an `APIException` if an error occurs during processing, ensuring structured error responses.