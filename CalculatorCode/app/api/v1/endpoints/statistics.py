from fastapi import APIRouter, Depends
from app.models.calculator import RegressionInput, CorrelationInput, TTestInput, ListInput, DbInput
from app.services.stats_service import stats_service, StatsService
from app.services.data_service import data_service, DataService
from app.services.validation_service import validation_service, ValidationService # Import new service
from app.core.exceptions import APIException
import pandas as pd

router = APIRouter()

# This endpoint now depends on the new ValidationService.
# FastAPI will automatically create an instance of it and pass it to the function.
@router.post("/regression/ols", summary="Perform OLS regression")
def perform_regression(
    payload: RegressionInput, 
    validator: ValidationService = Depends(lambda: validation_service),
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    """
    Performs an Ordinary Least Squares (OLS) regression.
    This endpoint first calls the ValidationService to perform deep checks
    on the input data before handing it off to the StatsService for calculation.
    """
    try:
        # 1. Call the validation service first. This connects this endpoint
        #    to both the model and the validation logic.
        validator.validate_regression_inputs(payload)
        
        # 2. If validation passes, proceed with the calculation service.
        summary = stats_svc.perform_ols_regression(
            db_path=payload.db_path, 
            table_name=payload.table_name, 
            dependent_var=payload.dependent_var, 
            independent_vars=payload.independent_vars
        )
        return {"analysis_type": "OLS Regression", "results_summary": summary}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))

@router.post("/correlation", summary="Calculate a correlation matrix")
def get_correlation_matrix(
    payload: CorrelationInput, 
    validator: ValidationService = Depends(lambda: validation_service),
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    """
    Calculates the correlation matrix for a set of columns.
    This also uses the ValidationService for pre-computation checks.
    """
    try:
        # 1. Validate inputs against the actual data.
        validator.validate_correlation_inputs(payload)
        
        # 2. Perform calculation.
        matrix = stats_svc.calculate_correlation_matrix(
            db_path=payload.db_path, 
            table_name=payload.table_name, 
            columns=payload.columns
        )
        return {"analysis_type": "Correlation Matrix", "table": payload.table_name, "correlation_matrix": matrix}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))

# Other endpoints remain the same...

@router.post("/test/independent_ttest", summary="Perform an independent t-test")
def perform_ttest(payload: TTestInput, service: StatsService = Depends(lambda: stats_service)):
    try:
        results = service.perform_independent_ttest(payload.sample1, payload.sample2)
        return {"analysis_type": "Independent Two-Sample T-Test", "results": results}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))

