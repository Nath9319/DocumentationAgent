# Documentation for `ValidationService`

```python
class ValidationService:
    """
    A service dedicated to performing complex, cross-service validations
    that go beyond simple model field checks. This service connects models
    to the data layer to ensure requests are not just well-formed, but
    also logically valid against the actual data.
    """

    def __init__(self, data_svc: DataService = data_service):
        """
        Initializes the ValidationService with a dependency on the DataService.

        This constructor sets up the ValidationService instance by accepting an 
        optional DataService instance. If no instance is provided, a default 
        instance is used.

        Parameters:
        ----------
        data_svc : DataService, optional
            An instance of DataService that the ValidationService will use for 
            data-related operations. If not specified, the default instance 
            (data_service) will be utilized.

        Example:
        --------
        >>> validation_service = ValidationService()
        >>> validation_service_with_custom_data_svc = ValidationService(custom_data_service)
        """
        self.data_svc = data_svc

    def validate_regression_inputs(self, payload: RegressionInput):
        """
        Validates the inputs for regression analysis by checking the existence and data type 
        of specified columns in a database table.

        This method connects the `RegressionInput` model with the `DataService` to perform 
        comprehensive validation of the regression inputs.

        Args:
            payload (RegressionInput): The Pydantic model containing the request data, 
                                       including the database path, table name, dependent variable, 
                                       and independent variables.

        Raises:
            DataError: If any of the following validation checks fail:
                - The specified columns do not exist in the database table.
                - The specified columns are not of numeric type.
                - The specified columns contain only null values.

        Returns:
            bool: Returns `True` if all validation checks pass.

        Example:
            try:
                is_valid = validation_service.validate_regression_inputs(payload)
            except DataError as e:
                print(f"Validation error: {e.detail}")

        Notes:
            This method performs the following steps:
            1. Retrieves the DataFrame from the specified SQLite database and table.
            2. Checks each variable (dependent and independent) for existence in the DataFrame.
            3. Validates that each variable is numeric and contains valid data.
        """
        print(f'Performing deep validation for regression on table: {payload.table_name}')
        df = self.data_svc.get_dataframe_from_sqlite(payload.db_path, payload.table_name)
        all_vars = [payload.dependent_var] + payload.independent_vars
        for var in all_vars:
            if var not in df.columns:
                raise DataError(f"Column '{var}' not found in table '{payload.table_name}'.")
            if not pd.api.types.is_numeric_dtype(df[var]):
                raise DataError(f"Column '{var}' must be numeric for regression analysis.")
            if df[var].isnull().all():
                raise DataError(f"Column '{var}' contains no valid data; all values are null.")
        print('Regression input validation successful.')
        return True

    def validate_correlation_inputs(self, payload: CorrelationInput):
        """
        Validates that the specified columns for a correlation analysis exist in the provided DataFrame 
        and are of numeric type.

        This method performs the following checks:
        - Ensures that at least two numeric columns are available for correlation analysis.
        - Confirms that each specified column exists in the DataFrame.
        - Validates that each specified column is numeric.

        Args:
            payload (CorrelationInput): The Pydantic model containing the parameters for correlation analysis,
                                        including the database path, table name, and columns to check.

        Raises:
            DataError: If any of the validation checks fail, indicating issues such as:
                - Fewer than two numeric columns available for correlation.
                - Specified columns not found in the DataFrame.
                - Specified columns not being of numeric type.

        Returns:
            bool: Returns `True` if all validations pass successfully.

        Example:
            try:
                validation_service.validate_correlation_inputs(correlation_input)
            except DataError as e:
                print(f"Validation error: {e.detail}")

        Notes:
            - The method retrieves the DataFrame from a SQLite database using the provided database path and table name.
            - If no columns are specified in the payload, the method defaults to checking all numeric columns in the DataFrame.
        """
        print(f'Performing deep validation for correlation on table: {payload.table_name}')
        df = self.data_svc.get_dataframe_from_sqlite(payload.db_path, payload.table_name)
        columns_to_check = payload.columns
        if not columns_to_check:
            columns_to_check = df.select_dtypes(include='number').columns.tolist()
        if len(columns_to_check) < 2:
            raise DataError('Correlation analysis requires at least two