# Documentation for `SingleInput`

```python
class SingleInput(BaseModel):
    """Model for operations requiring a single number.

    Attributes:
        number (float): The single numeric input required for the operation.
    """
    number: float
```

### Documentation for `SingleInput` Class

#### Overview
The `SingleInput` class is a model designed to represent operations that require a single numeric input. It inherits from `BaseModel`, which may provide additional functionality or structure common to all models in the application.

#### Attributes
- **number (float)**: This attribute holds the single numeric value necessary for the operation. It is expected to be a floating-point number.

#### Usage
This class can be instantiated with a floating-point number to represent the input for various calculations or operations that require only one numeric value. 

#### Example
```python
single_input = SingleInput(number=42.0)
```

In this example, an instance of `SingleInput` is created with the number `42.0`, which can then be used in subsequent operations that require a single input.