# Documentation for `DataError.__init__`

```python
def __init__(self, detail: str='An error occurred while processing data.'):
    super().__init__(status_code=400, detail=detail)
```

### Documentation for `DataError.__init__`

#### Method: `__init__`

**Category:** Method  
**File Path:** `app/core/exceptions.py`  
**Lines:** 18 to 19  

#### Description
The `__init__` method initializes a new instance of the `DataError` class, which is a custom exception used to indicate errors that occur during data processing. This method sets a default error message and a status code for the exception.

#### Parameters
- **detail** (`str`, optional): A descriptive message that provides details about the error. Defaults to `'An error occurred while processing data.'`.

#### Inheritance
This method calls the `__init__` method of its superclass, passing a fixed `status_code` of `400` along with the provided `detail` message. This indicates a client-side error related to the request.

#### Example Usage
```python
try:
    # Some data processing logic
    raise DataError("Invalid data format.")
except DataError as e:
    print(e.detail)  # Output: Invalid data format.
```

#### Notes
- The `DataError` class is typically used in scenarios where data validation or processing fails, allowing for clear communication of the error to the caller.
- The default message can be overridden by providing a custom message when raising the exception.