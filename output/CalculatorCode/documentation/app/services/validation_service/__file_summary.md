# File Summary

# 📌 Basic Information

## Title & Overview
**File Name**: `validation_service.py`  
**Overview**: The `validation_service.py` file contains the `ValidationService` class, which is designed to perform complex validations on incoming data across various services. It ensures that data adheres to logical constraints and integrity standards before further processing.

## Purpose
The primary purpose of the `ValidationService` is to validate data inputs from user requests or other services, ensuring that they are well-formed and logically valid against the actual data stored in the system. This service plays a crucial role in maintaining data integrity and consistency throughout the application.

## Scope
The scope of this file includes the implementation of the `ValidationService` class and its associated methods, which validate inputs for correlation and regression analyses. The service interacts with a data layer to retrieve necessary data for validation checks.

---

# ⚙️ Technical or Functional Details

## Architecture / Design
The `ValidationService` class is designed to act as a mediator between the data layer and application logic. It relies on an instance of the `DataService` class to fetch data from a SQLite database and performs validation checks on the data retrieved. The class includes methods for validating correlation and regression input data, ensuring that the specified columns exist and are of numeric types.

## Features & Functions
- **ValidationService Class**: Main class responsible for validating incoming data.
  - **Methods**:
    - `__init__(data_service: DataService)`: Initializes the `ValidationService` with a `DataService` instance.
    - `validate_correlation_inputs(payload: CorrelationInput)`: Validates inputs for correlation analysis, checking for column existence and numeric data types.
    - `validate_regression_inputs(payload: RegressionInput)`: Validates inputs for regression analysis, ensuring specified columns exist and are numeric.

## Requirements
- **Dependencies**:
  - `DataService`: An instance of this class is required for data retrieval.
  - `CorrelationInput`: A Pydantic model used for validating correlation analysis inputs.
  - `RegressionInput`: A Pydantic model used for validating regression analysis inputs.
  - `pandas`: Utilized for handling data as DataFrames and performing data type checks.

---

# 🚀 Setup and Usage

## Installation Instructions
- Ensure that the necessary dependencies, including `pandas` and the Pydantic models, are installed in your Python environment.

## Configuration Settings
- The `ValidationService` requires a properly configured instance of `DataService` that can connect to the relevant data sources (e.g., SQLite databases).

## Usage Guidelines
1. **Instantiate the ValidationService**:
   ```python
   from app.services.validation_service import ValidationService
   from app.services.data_service import DataService

   data_service = DataService()  # Initialize DataService
   validation_service = ValidationService(data_service)  # Initialize ValidationService
   ```

2. **Validate Correlation Inputs**:
   ```python
   from app.models import CorrelationInput

   payload = CorrelationInput(column_names=['col1', 'col2'])  # Create payload
   validation_service.validate_correlation_inputs(payload)  # Validate inputs
   ```

3. **Validate Regression Inputs**:
   ```python
   from app.models import RegressionInput

   payload = RegressionInput(dependent='target', independent=['feature1', 'feature2'])  # Create payload
   validation_service.validate_regression_inputs(payload)  # Validate inputs
   ```

By following these guidelines, users can effectively utilize the `ValidationService` to ensure data integrity and consistency in their applications.