# Documentation for `get_z_scores`

```python
def get_z_scores(payload: ZScoreInput, stats_svc: StatsService=Depends(lambda: stats_service)):
    """
    Calculate z-scores based on the provided input data.

    This function receives a payload containing data for which z-scores 
    are to be calculated. It utilizes the `StatsService` to perform the 
    calculation and returns the results in a structured format. In case 
    of any errors during the calculation, an `APIException` is raised 
    with an appropriate status code and error message.

    Parameters:
    ----------
    payload : ZScoreInput
        An instance of `ZScoreInput` containing the data for z-score 
        calculation. The `data` attribute of this instance is expected 
        to be a list or array-like structure of numerical values.

    stats_svc : StatsService, optional
        An instance of `StatsService` used to perform the z-score 
        calculations. This parameter is automatically provided by 
        dependency injection.

    Returns:
    -------
    dict
        A dictionary containing the analysis type and the calculated 
        z-scores. The structure of the returned dictionary is as follows:
        {
            'analysis_type': 'Z-Scores',
            'z_scores': <calculated_z_scores>
        }

    Raises:
    ------
    APIException
        If an error occurs during the z-score calculation, an 
        `APIException` is raised with a status code of 400 and a 
        detailed error message.

    Example:
    --------
    To call this endpoint, send a POST request to `/z_scores` with 
    a JSON body containing the data for z-score calculation:
    
    ```json
    {
        "data": [10, 20, 30, 40, 50]
    }
    ```

    The response will be structured as follows:
    
    ```json
    {
        "analysis_type": "Z-Scores",
        "z_scores": [<calculated_z_scores>]
    }
    ```

    Note:
    -----
    Ensure that the input data is valid and numerical to avoid 
    exceptions during processing.
    """
    try:
        z_scores = stats_svc.calculate_z_scores(payload.data)
        return {'analysis_type': 'Z-Scores', 'z_scores': z_scores}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
``` 

### Documentation Summary:
The `get_z_scores` function is designed to calculate z-scores from a given dataset. It handles input through a structured payload and utilizes a service class for the calculation. In the event of an error, it raises a custom API exception to ensure that errors are communicated clearly to the API consumer. The documentation provides detailed information on parameters, return values, exceptions, and usage examples to facilitate understanding and implementation.