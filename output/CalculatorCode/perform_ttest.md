# Documentation for `perform_ttest`

```python
def perform_ttest(payload: TTestInput, service: StatsService = Depends(lambda: stats_service)):
    """
    Perform an independent two-sample t-test on the provided samples.

    This function takes a payload containing two samples and uses the 
    specified statistics service to perform the t-test. It returns the 
    results of the analysis in a structured format.

    Args:
        payload (TTestInput): An object containing two samples (sample1 and sample2) 
                              for the t-test.
        service (StatsService, optional): An instance of StatsService to perform 
                                           the statistical analysis. Defaults to 
                                           the injected stats_service.

    Returns:
        dict: A dictionary containing the analysis type and the results of the t-test.

    Raises:
        APIException: If an error occurs during the t-test execution, a 400 status 
                      code is raised with the error details.

    Example:
        >>> payload = TTestInput(sample1=[1, 2, 3], sample2=[4, 5, 6])
        >>> response = perform_ttest(payload)
        >>> print(response)
        {"analysis_type": "Independent Two-Sample T-Test", "results": {...}}
    """
    try:
        results = service.perform_independent_ttest(payload.sample1, payload.sample2)
        return {"analysis_type": "Independent Two-Sample T-Test", "results": results}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
``` 

### Explanation of the Documentation:
- **Function Purpose:** The docstring clearly states the purpose of the function, which is to perform an independent two-sample t-test.
- **Arguments:** Each argument is described, including its type and purpose.
- **Return Value:** The return value is specified, detailing the structure of the returned dictionary.
- **Error Handling:** The docstring mentions the exception that may be raised, providing clarity on error handling.
- **Example Usage:** An example is included to demonstrate how to use the function, which aids in understanding its application.