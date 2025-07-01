# Documentation for `LoanPaymentInput`

### LoanPaymentInput

**Description:**
The `LoanPaymentInput` class serves as a model for calculating loan payments. It encapsulates the necessary attributes and methods required to represent and manipulate the input data for loan payment calculations, ensuring that the data adheres to specific validation rules.

**Parameters/Attributes:**
- `principal` (`float`): The total amount of the loan that is being borrowed.
- `annual_rate` (`float`): The annual interest rate applied to the loan, expressed as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of payments to be made over the life of the loan.

**Expected Input:**
- `principal` must be a positive float, representing the loan amount.
- `annual_rate` should be a non-negative float, where 0.0 indicates no interest.
- `num_payments` must be a positive integer, indicating the number of payment periods.

**Returns:**
None (the class does not return a value but provides a structure for loan payment input).

**Detailed Logic:**
- The `LoanPaymentInput` class inherits from `BaseModel`, which likely provides foundational functionality for data validation and management.
- It utilizes the `Field` function to define its attributes, which may include validation rules such as type checking and constraints on the values (e.g., ensuring that `principal` is positive).
- The class is designed to encapsulate the input data for loan payment calculations, making it easier to manage and validate the data before performing any calculations related to loan payments.
- The interaction with `BaseModel` and `Field` suggests that this class is part of a larger framework that may include features like serialization, deserialization, and integration with databases or APIs.