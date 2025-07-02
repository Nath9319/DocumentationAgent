### ValidationService

**Description:**  
A service dedicated to performing complex, cross-service validations that go beyond simple model field checks. This service connects models to the data layer to ensure requests are not just well-formed, but also logically valid against the actual data.

**Parameters / Attributes:**  
| Name          | Type                | Description                                                                 |
|---------------|---------------------|-----------------------------------------------------------------------------|
| models        | list                | A list of models to validate against the data layer.                       |
| data_layer    | DataLayerInterface   | An interface to interact with the underlying data layer for validation.     |
| request_data  | dict                | The data from the request that needs to be validated.                      |

**Expected Input:**  
• `models` should be a list of model instances.  
• `data_layer` must implement the required methods for data access.  
• `request_data` should be a dictionary containing the fields to validate.

**Returns:**  
`bool` – indicates whether the validation was successful (True) or failed (False).

**Detailed Logic:**  
• The service initializes with the provided models, data layer, and request data.  
• It iterates through each model to perform field-level validations.  
• For each model, it checks the logical consistency of the request data against the actual data retrieved from the data layer.  
• If all validations pass, it returns True; otherwise, it returns False.

**Raises / Errors:**  
• Raises `ValidationError` if the validation process encounters issues with the request data.  
• Raises `DataLayerError` if there are problems accessing the data layer.

**Usage Example:**  
```python
validation_service = ValidationService(models=[UserModel, OrderModel], data_layer=my_data_layer, request_data=request_payload)
is_valid = validation_service.validate()
```