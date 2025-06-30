# Documentation for `CorrelationInput`

```python
class CorrelationInput(BaseModel):
    """
    Model for correlation matrix input.

    This class represents the input required to generate a correlation matrix.
    It ensures that at least two columns are specified when provided. The input
    consists of a table name, an optional list of column names, and a database path.

    Attributes:
        table_name (str): The name of the table from which to derive the correlation matrix.
        columns (Optional[List[str]]): A list of column names to be included in the correlation matrix.
            Must contain at least two elements if specified.
        db_path (str): The path to the database file. Defaults to 'data/sample_database.db'.

    Methods:
        check_min_columns(cls, v): Validates that the number of columns specified is at least two.
    """

    table_name: str
    columns: Optional[List[str]] = None
    db_path: str = 'data/sample_database.db'

    @field_validator('columns')
    @classmethod
    def check_min_columns(cls, v):
        """
        Validate the number of columns specified for a correlation matrix.

        This class method checks if the provided value `v` (representing the columns)
        contains at least two elements. If `v` is not None and contains fewer than 
        two columns, a ValueError is raised with an appropriate message.

        Parameters:
            cls (Type[CorrelationInput]): The class that this method is bound to.
            v (Optional[List[Any]]): The value representing the columns to be validated.

        Returns:
            Optional[List[Any]]: The validated columns if the check passes.

        Raises:
            ValueError: If fewer than two columns are specified.
        """
        if v is not None and len(v) < 2:
            raise ValueError('At least two columns must be specified for a correlation matrix.')
        return v
``` 

### Summary of Documentation:
- **Purpose**: The class docstring provides a clear overview of the `CorrelationInput` class, detailing its role in managing input for correlation matrix generation.
- **Attributes**: Each attribute is described with its type and purpose, ensuring users understand what data is required.
- **Methods**: The method `check_min_columns` is documented to explain its functionality, parameters, return values, and exceptions raised, aligning with best practices for clarity and usability.