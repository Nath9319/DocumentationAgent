# Documentation for `LoanPaymentInput`

### LoanPaymentInput

**Description:**
`LoanPaymentInput` is a class that serves as a model for capturing and validating input related to loan payment calculations. It extends the `BaseModel` class, inheriting its foundational properties and methods while adding specific fields that pertain to loan payment details. This class is designed to ensure that all necessary information for processing loan payments is collected and validated before further calculations are performed.

**Parameters/Attributes:**
- `loan_amount` (`Field`): Represents the total amount of the loan. This field is required and must be a positive number.
- `interest_rate` (`Field`): Represents the annual interest rate of the loan as a percentage. This field is required and must be a non-negative number.
- `payment_term` (`Field`): Represents the duration over which the loan will be repaid, typically in months. This field is required and must be a positive integer.

**Expected Input:**
- `loan_amount` should be a positive numeric value indicating the total loan amount.
- `interest_rate` should be a non-negative numeric value representing the annual interest rate (e.g., 5 for 5%).
- `payment_term` should be a positive integer indicating the number of months over which the loan will be repaid.

**Returns:**
`None`: The class does not return a value upon instantiation but initializes an object that encapsulates loan payment input data.

**Detailed Logic:**
- Upon instantiation, `LoanPaymentInput` initializes its attributes using instances of the `Field` class for each of the required loan parameters.
- Each `Field` instance is configured with validation rules to ensure that the input data meets the specified criteria (e.g., positive values for `loan_amount` and `payment_term`, and a non-negative value for `interest_rate`).
- The class leverages the inherited functionality from `BaseModel`, allowing it to maintain a consistent structure and behavior with other models in the application.
- The validation mechanisms provided by the `Field` class ensure that any data assigned to these attributes is checked for correctness, promoting data integrity within the loan payment processing workflow.

---
*Generated with 100% context confidence*
