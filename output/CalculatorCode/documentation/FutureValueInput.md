# Documentation for `FutureValueInput`

```markdown
### FutureValueInput

**Description:**  
The `FutureValueInput` class serves as a model for calculating the future value of cash flows. It incorporates validation rules to ensure that cash flow conventions are adhered to, particularly focusing on the representation of cash outflows as negative values.

**Parameters/Attributes:**
- `cash_flows` (`list` of `float`): A list of cash flow values that represent the inflows and outflows over a specified period. This attribute is essential for future value calculations.
- `interest_rate` (`float`): The interest rate applied to the cash flows, expressed as a decimal (e.g., 0.05 for 5%).
- `time_period` (`int`): The number of periods (e.g., years) over which the cash flows will be evaluated for future value.

**Expected Input:**  
- `cash_flows` should contain a mix of positive and negative floats, where positive values represent cash inflows and negative values represent cash outflows. It is crucial that all cash outflows are input as negative numbers to comply with financial conventions.
- `interest_rate` should be a non-negative float, where 0.0 indicates no interest.
- `time_period` should be a positive integer representing the duration for which the future value is calculated.

**Returns:**  
None. The class does not return a value directly but provides methods to compute the future value based on the provided attributes.

**Detailed Logic:**  
- The `FutureValueInput` class initializes with attributes for cash flows, interest rate, and time period.
- It includes a method, `cash_outflow_must_be_negative`, which validates that all cash outflows in the `cash_flows` list are negative. This method checks each value in the list and raises an error if any cash outflow is found to be positive, ensuring compliance with standard financial practices.
- The class is designed to facilitate future value calculations by ensuring that the input data adheres to expected financial norms, thus preventing errors in financial modeling.
- The class does not interact with external modules but relies on its internal validation logic to maintain data integrity.
```