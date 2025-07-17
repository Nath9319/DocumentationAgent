# Documentation for `FutureValueInput`

### FutureValueInput

**Description:**
`FutureValueInput` is a class designed to represent the input parameters required for calculating the future value of an investment or financial asset. It extends the `BaseModel`, inheriting its foundational properties and methods, while also defining specific fields relevant to future value calculations. This class encapsulates the necessary attributes and validation logic to ensure that the input data is structured and valid for further processing.

**Parameters/Attributes:**
- `investment_amount` (`Field`): A field representing the initial amount of money invested. It is expected to be a positive numeric value.
- `interest_rate` (`Field`): A field that holds the annual interest rate as a percentage. It should be a non-negative numeric value.
- `time_period` (`Field`): A field indicating the duration for which the investment is held, typically measured in years. It is expected to be a positive integer.

**Expected Input:**
- The `investment_amount` must be a positive numeric value, representing the initial investment.
- The `interest_rate` should be a non-negative numeric value, indicating the annual interest rate expressed as a percentage.
- The `time_period` must be a positive integer, representing the number of years the investment will be held.

**Returns:**
`None`: The class does not return a value upon instantiation but initializes an object that encapsulates the input parameters for future value calculations.

**Detailed Logic:**
- Upon instantiation, `FutureValueInput` initializes its fields using the `Field` class, which manages the properties and validation for each input parameter.
- The `investment_amount`, `interest_rate`, and `time_period` fields are defined with specific validation rules to ensure that the values assigned to them are appropriate for future value calculations.
- The class leverages the inherited functionality from `BaseModel`, allowing for consistent handling of common behaviors and attributes across different model classes.
- The validation logic ensures that any attempts to assign invalid values to the fields will be caught, promoting data integrity and reliability in future calculations.

---
*Generated with 100% context confidence*
