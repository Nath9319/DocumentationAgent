# Documentation for `CalculationError`

```markdown
### CalculationError

**Description:**  
The `CalculationError` class is a custom exception designed to handle errors that arise specifically during calculation processes within the application. It provides a mechanism to raise exceptions with meaningful messages that can help identify and troubleshoot issues related to calculations.

**Parameters/Attributes:**
- `message` (`str`): A descriptive message that explains the reason for the exception being raised.

**Expected Input:**  
- The `message` parameter should be a non-empty string that clearly articulates the nature of the calculation error. It is important that the message provides sufficient detail to assist users or developers in understanding the issue at hand.

**Returns:**  
`None`: The class does not return any value, as it is used to create an instance of the exception.

**Detailed Logic:**  
- The `CalculationError` class inherits from the base exception class, and its `__init__` method is invoked when an instance of the exception is created. This method accepts a single argument, `message`, which is stored as part of the exception instance.
- The `__init__` method typically calls the parent class's `__init__` method to ensure that the base exception is initialized correctly with the provided message.
- By using this custom exception, developers can raise `CalculationError` instances in their code whenever a calculation-related issue occurs, allowing for more informative error handling and debugging.
- This class operates independently without dependencies on other modules or functions, making it a self-contained component for managing calculation errors.
```