# Documentation for `CalculationError`

### CalculationError

**Description:**
`CalculationError` is a custom exception class designed to handle errors that occur during mathematical calculations within the application. This class extends the base exception class, allowing it to be raised and caught specifically for calculation-related issues, providing clearer error handling in the codebase.

**Parameters/Attributes:**
None.

**Expected Input:**
- This class does not require any specific input parameters upon instantiation. However, it can accept a message string that describes the error when raised.

**Returns:**
None.

**Detailed Logic:**
- The `CalculationError` class inherits from Python's built-in `Exception` class, utilizing the `super().__init__` method to initialize the base class. This allows it to leverage the standard exception handling mechanisms while providing a specific context for calculation errors.
- When an instance of `CalculationError` is raised, it can include a custom error message that describes the nature of the calculation failure, aiding developers in debugging and error resolution.