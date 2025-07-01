# Documentation for `FutureValueInput.cash_outflow_must_be_negative`

```markdown
### FutureValueInput.cash_outflow_must_be_negative()

**Description:**  
This method enforces a validation rule that cash outflows must be represented as negative values. It is a part of the `FutureValueInput` class, which likely deals with financial calculations related to future value projections.

**Parameters/Attributes:**  
None

**Expected Input:**  
- The method expects cash outflow values to be provided in a context where they can be validated. Specifically, any cash outflow should be input as a negative number to comply with financial conventions.

**Returns:**  
None

**Detailed Logic:**  
- The method checks the value of cash outflows and ensures that they are negative. If a cash outflow is provided as a positive value, it indicates an error in the financial input, as cash outflows typically represent expenses or payments made, which should logically be negative.
- This method does not call any external functions or interact with other components, as it solely focuses on validating the sign of the cash outflow value.
```