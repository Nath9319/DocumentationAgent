class APIException(Exception):
    """
    Custom base exception class for the API.
    This allows us to create a custom exception handler in main.py
    to return structured JSON error messages.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

# We can define specific exceptions that inherit from this base class
class CalculationError(APIException):
    def __init__(self, detail: str = "A calculation error occurred."):
        super().__init__(status_code=400, detail=detail)

class DataError(APIException):
    def __init__(self, detail: str = "An error occurred while processing data."):
        super().__init__(status_code=400, detail=detail)

