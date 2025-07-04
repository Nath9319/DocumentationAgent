from fastapi import APIRouter, Depends
from app.models.calculator import RegressionInput, CorrelationInput, TTestInput, DescriptiveStatsInput, ConfidenceIntervalInput, ZScoreInput
from app.services.stats_service import stats_service, StatsService
from app.services.validation_service import validation_service, ValidationService
from app.core.exceptions import APIException
from app.models.calculator import StdDevInput
from app.services.financial_service import financial_service, FinancialService
from fastapi import APIRouter, Depends
from app.services.financial_service import financial_service, FinancialService  # Import FinancialService
from app.models.calculator import FutureValueInput, LoanPaymentInput, PresentValueInput  # Import relevant models
from app.core.exceptions import APIException  # For custom error handling
from fastapi import APIRouter, Depends
from app.services.stats_service import stats_service  # Import StatsService
from app.models.calculator import RegressionInput  # Import relevant input model

router = APIRouter()


@router.post("/regression/ols", summary="Perform OLS regression")
def perform_regression(
    payload: RegressionInput,
    stats_svc: StatsService = Depends(lambda: stats_service)
):
    try:
        # Perform the regression using StatsService, which internally uses DataService
        summary = stats_svc.perform_ols_regression(
            db_path=payload.db_path,
            table_name=payload.table_name,
            dependent_var=payload.dependent_var,
            independent_vars=payload.independent_vars
        )
        return {"analysis_type": "OLS Regression", "results_summary": summary}
    except Exception as e:
        raise APIException(status_code=400, detail=str(e))
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

# --- Financial Endpoints ---
# Endpoint for calculating Future Value
@router.post("/calculate-future-value", summary="Calculate Future Value of an Investment")
def calculate_future_value(
    payload: FutureValueInput, 
    financial_svc: FinancialService = Depends(lambda: financial_service)
):
    """
    Endpoint to calculate the future value of an investment.
    Takes rate, number of periods, payment, and present value as inputs.
    """
    try:
        future_value = financial_svc.calculate_future_value(
            rate=payload.rate,
            nper=payload.nper,
            pmt=payload.pmt,
            pv=payload.pv
        )
        return {"analysis_type": "Future Value", "future_value": future_value}
    except ValueError as e:
        raise APIException(status_code=400, detail=str(e))

# Endpoint for calculating Present Value
@router.post("/calculate-present-value", summary="Calculate Present Value of an Investment")
def calculate_present_value(
    payload: PresentValueInput, 
    financial_svc: FinancialService = Depends(lambda: financial_service)
):
    """
    Endpoint to calculate the present value of an investment.
    Takes rate, number of periods, payment, and future value as inputs.
    """
    try:
        present_value = financial_svc.calculate_present_value(
            rate=payload.rate,
            nper=payload.nper,
            pmt=payload.pmt,
            fv=payload.fv
        )
        return {"analysis_type": "Present Value", "present_value": present_value}
    except ValueError as e:
        raise APIException(status_code=400, detail=str(e))

# Endpoint for calculating Loan Payment
@router.post("/calculate-loan-payment", summary="Calculate Loan Payment")
def calculate_loan_payment(
    payload: LoanPaymentInput, 
    financial_svc: FinancialService = Depends(lambda: financial_service)
):
    """
    Endpoint to calculate the periodic payment for a loan.
    Takes rate, number of periods, and present value as inputs.
    """
    try:
        loan_payment = financial_svc.calculate_payment(
            rate=payload.rate,
            nper=payload.nper,
            pv=payload.pv
        )
        return {"analysis_type": "Loan Payment", "loan_payment": loan_payment}
    except ValueError as e:
        raise APIException(status_code=400, detail=str(e))