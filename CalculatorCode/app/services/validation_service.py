import pandas as pd
from typing import List
from app.models.calculator import RegressionInput, CorrelationInput
from app.services.data_service import data_service, DataService
from app.core.exceptions import DataError

class ValidationService:
    """
    A service dedicated to performing complex, cross-service validations
    that go beyond simple model field checks. This service connects models
    to the data layer to ensure requests are not just well-formed, but
    also logically valid against the actual data.
    """

    def __init__(self, data_svc: DataService = data_service):
        """
        Initializes the validation service with a dependency on the DataService.
        """
        self.data_svc = data_svc

    def validate_regression_inputs(self, payload: RegressionInput):
        """
        Connects to the database to validate that columns for a regression
        analysis exist and are numeric.

        This function is a perfect example of connecting a model (RegressionInput)
        with another service (DataService) for deep validation.

        Args:
            payload (RegressionInput): The Pydantic model containing the request data.

        Raises:
            DataError: If any validation check fails.
        """
        print(f"Performing deep validation for regression on table: {payload.table_name}")
        
        # Fetch the entire dataframe using the data service
        df = self.data_svc.get_dataframe_from_sqlite(payload.db_path, payload.table_name)
        
        all_vars = [payload.dependent_var] + payload.independent_vars
        
        for var in all_vars:
            # 1. Check if column exists
            if var not in df.columns:
                raise DataError(f"Column '{var}' not found in table '{payload.table_name}'.")
            
            # 2. Check if the column data is numeric
            if not pd.api.types.is_numeric_dtype(df[var]):
                raise DataError(f"Column '{var}' must be numeric for regression analysis.")
            
            # 3. Check for sufficient non-null data
            if df[var].isnull().all():
                raise DataError(f"Column '{var}' contains no valid data; all values are null.")

        print("Regression input validation successful.")
        return True
        
    def validate_correlation_inputs(self, payload: CorrelationInput):
        """
        Validates that columns for a correlation analysis exist and are numeric.
        
        Args:
            payload (CorrelationInput): The Pydantic model for correlation.
            
        Raises:
            DataError: If validation fails.
        """
        print(f"Performing deep validation for correlation on table: {payload.table_name}")
        df = self.data_svc.get_dataframe_from_sqlite(payload.db_path, payload.table_name)

        columns_to_check = payload.columns
        if not columns_to_check:
            # If no columns are specified, use all numeric columns from the dataframe.
            columns_to_check = df.select_dtypes(include='number').columns.tolist()

        if len(columns_to_check) < 2:
            raise DataError("Correlation analysis requires at least two numeric columns.")
            
        for col in columns_to_check:
            if col not in df.columns:
                 raise DataError(f"Column '{col}' not found in table '{payload.table_name}'.")
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise DataError(f"Column '{col}' must be numeric for correlation analysis.")

        print("Correlation input validation successful.")
        return True


# Instantiate a singleton of the service to be used as a dependency
validation_service = ValidationService()
