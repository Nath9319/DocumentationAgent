# Documentation for `calculate_std_deviation`

```python
def calculate_std_deviation(payload: StdDevInput, stats_svc: StatsService=Depends(lambda: stats_service)):
    """
    Calculate the standard deviation of a given dataset.

    This function is an endpoint for calculating the standard deviation 
    based on the input data provided in the payload. It utilizes the 
    `StatsService` to perform the calculation and returns the result in 
    a structured format. If an error occurs during the calculation, 
    an `APIException` is raised with a 400 status code.

    Parameters:
    ----------
    payload : StdDevInput
        An instance of `StdDevInput` containing the dataset for which 
        the standard deviation is to be calculated. The `data` attribute 
        of this instance should be a list of numerical values.

    stats_svc : StatsService, optional
        An instance of `StatsService` that provides the method to 
        calculate the standard deviation. This parameter is injected 
        using FastAPI's dependency injection system.

    Returns:
    -------
    dict
        A dictionary containing the analysis type and the calculated 
        standard deviation. The structure of the returned dictionary is:
        {
            'analysis_type': 'Standard Deviation',
            'result': <calculated_std_dev>
        }

    Raises:
    ------
    APIException
        If an error occurs during the calculation, an `APIException` 
        is raised with a status code of 400 and a detail message 
        describing the error.

    Example:
    --------
    To call this endpoint, send a POST request to `/standard_deviation` 
    with a JSON body containing the dataset:
    
    ```json
    {
        "data": [10, 12, 23, 23, 16, 23, 21, 16]
    }
    ```

    The response will be:
    
    ```json
    {
        "analysis_type": "Standard Deviation",
        "result": 4.898979485566356
    }
    ```

    Note:
    -----
    Ensure that the input data is valid and contains numerical values 
    to avoid exceptions during the calculation.
    """
    try:
        std_dev = stats_svc.calculate_standard_deviation(payload.data)
        return {'analysis_type': 'Standard Deviation', 'result': std_dev}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
``` 

### Summary of Documentation:
- **Function Purpose:** Calculates the standard deviation of a dataset.
- **Parameters:** Accepts a payload of type `StdDevInput` and an optional `StatsService`.
- **Returns:** A dictionary with the analysis type and the result.
- **Error Handling:** Raises an `APIException` for any calculation errors.
- **Example Usage:** Provides a sample request and response format.