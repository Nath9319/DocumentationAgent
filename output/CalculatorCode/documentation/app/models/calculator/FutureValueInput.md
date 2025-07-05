# Documentation for FutureValueInput

> ⚠️ **Quality Notice**: Documentation generated with 0% confidence. Some dependencies could not be fully resolved.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### FutureValueInput

**Description:**
The `FutureValueInput` class is designed to represent the input parameters required for calculating the future value of an investment or financial asset. It serves as a data model that encapsulates the necessary attributes, ensuring that the input data is structured and validated according to predefined rules.

**Parameters/Attributes:**
- `initial_investment` (`float`): The initial amount of money invested or the principal amount.
- `interest_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
- `years` (`int`): The number of years the money is invested or borrowed.

**Expected Input:**
- `initial_investment` should be a non-negative float, representing the starting amount of the investment.
- `interest_rate` should be a float between 0.0 and 1.0, where 0.0 indicates no interest.
- `years` should be a non-negative integer, representing the duration of the investment in years.

**Returns:**
`None`: The class does not return a value but initializes an instance with the specified attributes.

**Detailed Logic:**
- The `FutureValueInput` class inherits from `BaseModel`, which likely provides foundational functionality for data validation and management.
- It utilizes the `Field` class to define the attributes, allowing for additional validation rules and metadata to be applied to each attribute.
- The class ensures that the input data adheres to the expected types and constraints, facilitating reliable calculations for future value computations in financial applications.
- The design promotes encapsulation and reusability, making it easier to manage and validate input data across the application.

---
*Generated with 0% context confidence*
