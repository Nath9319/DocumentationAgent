# Documentation for `FutureValueInput`

### FutureValueInput

**Description:**
The `FutureValueInput` class serves as a model for calculating the future value of an investment based on specified cash flow conventions. It is designed to validate input parameters related to cash flows, ensuring that they conform to expected financial standards.

**Parameters/Attributes:**
- **Attributes:**
  - `cash_flows` (`List[float]`): A list of cash flow amounts, which can be positive (inflows) or negative (outflows).
  - `interest_rate` (`float`): The annual interest rate expressed as a decimal (e.g., 0.05 for 5%).
  - `periods` (`int`): The number of periods (e.g., years) over which the investment will grow.

**Expected Input:**
- The `cash_flows` attribute should be a list of floats, where each float represents a cash flow amount. The list can contain both positive and negative values.
- The `interest_rate` should be a non-negative float, representing the annual interest rate. A value of 0.0 indicates no growth.
- The `periods` should be a positive integer, indicating the total number of periods for the future value calculation.

**Returns:**
`None`: The class does not return a value directly; instead, it validates input data and prepares it for further calculations related to future value.

**Detailed Logic:**
- The `FutureValueInput` class inherits from `BaseModel`, which likely provides foundational functionality for data validation and management.
- It utilizes the `Field` function to define its attributes, ensuring that they are properly initialized and validated.
- The class employs `field_validator` to enforce constraints on the input data, such as ensuring that cash flows are in a valid format and that the interest rate and periods are within acceptable ranges.
- If any validation checks fail, a `ValueError` is raised, providing feedback on the nature of the input error.
- Overall, the class is structured to facilitate the future value calculation process by ensuring that all necessary parameters are correctly defined and validated before any calculations are performed.