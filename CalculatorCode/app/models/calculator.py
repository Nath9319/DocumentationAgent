from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import numpy as np
from pydantic import BaseModel
from typing import List


# This file defines the Pydantic models for request body validation.
# We've added custom @field_validator methods. These functions are automatically
# "called" by FastAPI and Pydantic when a request comes in, ensuring the data
# is valid before it reaches your business logic. This creates a strong
# interconnection between the models and the application's requirements.

# --- Base Models ---
class SingleInput(BaseModel):
    """Model for operations requiring a single number."""
    number: float

class DualInput(BaseModel):
    """Model for operations requiring two numbers."""
    number1: float
    number2: float

class ListInput(BaseModel):
    """Model for operations on a list of numbers."""
    data: List[float] = Field(..., min_length=1)

# --- Statistics Models ---
class TTestInput(BaseModel):
    """Model for an independent t-test. Validates that samples are not identical."""
    sample1: List[float] = Field(..., min_length=2)
    sample2: List[float] = Field(..., min_length=2)

    @field_validator('sample2')
    @classmethod
    def samples_must_not_be_identical(cls, v, values):
        # This function is called automatically during validation.
        # It checks if sample1 and sample2 are the same.
        if 'sample1' in values.data and v == values.data['sample1']:
            raise ValueError("Sample 1 and Sample 2 cannot be identical for a t-test.")
        return v

class RegressionInput(BaseModel):
    """Model for OLS regression. Ensures variables are distinct."""
    table_name: str
    dependent_var: str
    independent_vars: List[str] = Field(..., min_length=1)
    db_path: str = "data/sample_database.db"

    @field_validator('independent_vars')
    @classmethod
    def dependent_var_not_in_independent(cls, v, values):
        # This validator ensures the dependent variable isn't also in the list of independent variables.
        if 'dependent_var' in values.data and values.data['dependent_var'] in v:
            raise ValueError(f"The dependent variable '{values.data['dependent_var']}' cannot also be an independent variable.")
        return v

class CorrelationInput(BaseModel):
    """Model for correlation matrix. Ensures at least two columns are provided if specified."""
    table_name: str
    columns: Optional[List[str]] = None
    db_path: str = "data/sample_database.db"

    @field_validator('columns')
    @classmethod
    def check_min_columns(cls, v):
        if v is not None and len(v) < 2:
            raise ValueError("At least two columns must be specified for a correlation matrix.")
        return v


# --- Matrix Models ---
class MatrixInput(BaseModel):
    """Model for matrix operations. Includes validators and a helper function."""
    matrix: List[List[float]] = Field(..., min_length=1)

    @field_validator('matrix')
    @classmethod
    def matrix_must_be_square(cls, v):
        # This validator is called to ensure the matrix is square, a requirement
        # for determinant and inverse calculations. This is a direct link to the
        # logic in the 'stats_service.py'.
        if not v:
            raise ValueError("Matrix cannot be empty.")
        rows = len(v)
        for row in v:
            if len(row) != rows:
                raise ValueError("Matrix must be square (same number of rows and columns).")
        return v

    def to_numpy_array(self) -> np.ndarray:
        # This is a helper function that can be called by our services
        # to directly get a NumPy array from the validated input.
        return np.array(self.matrix)


# --- Financial Models ---
class FutureValueInput(BaseModel):
    """Model for Future Value calculation. Validates cash flow conventions."""
    rate: float = Field(..., gt=0, description="Interest rate per period (e.g., 0.05 for 5%)")
    nper: int = Field(..., gt=0, description="Total number of payment periods")
    pmt: float = Field(..., description="Payment made each period (conventionally negative for cash outflow)")
    pv: float = Field(..., description="Present value (conventionally negative for cash outflow)")

    @field_validator('pmt', 'pv')
    @classmethod
    def cash_outflow_must_be_negative(cls, v: float, info):
        # This validator enforces the financial convention that money you pay out (present value, payments)
        # should be represented as negative numbers.
        if v > 0:
            raise ValueError(f"'{info.field_name}' represents cash outflow and should be zero or negative.")
        return v

class LoanPaymentInput(BaseModel):
    """Model for Loan Payment calculation."""
    rate: float = Field(..., gt=0, description="Interest rate per period")
    nper: int = Field(..., gt=0, description="Total number of payment periods")
    pv: float = Field(..., gt=0, description="Present value or principal of the loan (must be positive)")


class StdDevInput(BaseModel):
    """Model for Standard Deviation calculation."""
    data: List[float]


class DescriptiveStatsInput(BaseModel):
    """Model for Descriptive Statistics calculation."""
    data: List[float]

class ZScoreInput(BaseModel):
    data: List[float]
    """Model for Z-Score calculation."""

class ConfidenceIntervalInput(BaseModel):
    """Model for Confidence Interval calculation."""
    data: List[float]
    confidence: float = 0.95  # Default to 95%



