from fastapi import APIRouter, Depends
from app.models.calculator import RegressionInput, CorrelationInput, TTestInput, DescriptiveStatsInput, ConfidenceIntervalInput, ZScoreInput
from app.services.stats_service import stats_service, StatsService
from app.services.validation_service import validation_service, ValidationService
from app.core.exceptions import APIException
from app.models.calculator import StdDevInput

router = APIRouter()

@router.post("/regression/ols", summary="Perform OLS regression")
def perform_regression(
    payload: RegressionInput, 
    validator: ValidationService = Depends(lambda: validation_service),
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    try:
        validator.validate_regression_inputs(payload)
        summary = stats_svc.perform_ols_regression(
            db_path=payload.db_path, 
            table_name=payload.table_name, 
            dependent_var=payload.dependent_var, 
            independent_vars=payload.independent_vars
        )
        return {"analysis_type": "OLS Regression", "results_summary": summary}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
# This endpoint performs an Ordinary Least Squares (OLS) regression.
# It uses the StatsService to perform the regression and returns the results.



@router.post("/correlation", summary="Calculate a correlation matrix")
def get_correlation_matrix(
    payload: CorrelationInput, 
    validator: ValidationService = Depends(lambda: validation_service),
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    try:
        validator.validate_correlation_inputs(payload)
        matrix = stats_svc.calculate_correlation_matrix(
            db_path=payload.db_path, 
            table_name=payload.table_name, 
            columns=payload.columns
        )
        return {
            "analysis_type": "Correlation Matrix",
            "table": payload.table_name,
            "correlation_matrix": matrix
        }
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
    # This endpoint calculates the correlation matrix for specified columns in a database table.
    # It uses the StatsService to perform the calculation and returns the results.


@router.post("/test/independent_ttest", summary="Perform an independent t-test")
def perform_ttest(
    payload: TTestInput, 
    service: StatsService = Depends(lambda: stats_service)
):
    try:
        results = service.perform_independent_ttest(payload.sample1, payload.sample2)
        return {"analysis_type": "Independent Two-Sample T-Test", "results": results}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
# This endpoint performs an independent two-sample t-test.
# It uses the StatsService to perform the test and returns the results.




@router.post("/standard_deviation", summary="Calculate standard deviation")
def calculate_std_deviation(
    payload: StdDevInput,
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    try:
        std_dev = stats_svc.calculate_standard_deviation(payload.data)
        return {"analysis_type": "Standard Deviation", "result": std_dev}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
# This endpoint is for calculating standard deviation.
# It uses the StatsService to perform the calculation and returns the result.
# The StdDevInput model is used to validate the input data.
# The APIException is raised if any error occurs during the process.

@router.post("/descriptive_stats", summary="Calculate descriptive statistics")
def get_descriptive_stats(
    payload: DescriptiveStatsInput,
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    try:
        result = stats_svc.calculate_descriptive_stats(payload.data)
        return {"analysis_type": "Descriptive Statistics", "results": result}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
# This endpoint calculates descriptive statistics for a list of numbers.
# It uses the StatsService to perform the calculation and returns the results.

@router.post("/confidence_interval", summary="Calculate confidence interval for mean")
def get_confidence_interval(
    payload: ConfidenceIntervalInput,
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    try:
        interval = stats_svc.calculate_confidence_interval(payload.data, payload.confidence)
        return {"analysis_type": "Confidence Interval", "results": interval}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
# This endpoint calculates the confidence interval for the mean of a list of numbers.
# It uses the StatsService to perform the calculation and returns the results.

@router.post("/z_scores", summary="Calculate z-scores")
def get_z_scores(
    payload: ZScoreInput,
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    try:
        z_scores = stats_svc.calculate_z_scores(payload.data)
        return {"analysis_type": "Z-Scores", "z_scores": z_scores}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
# This endpoint calculates the z-scores for a list of numbers.
# It uses the StatsService to perform the calculation and returns the z-scores.