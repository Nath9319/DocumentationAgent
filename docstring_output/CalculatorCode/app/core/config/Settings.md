### Settings

**Description:**  
Application settings, loaded from environment variables.

**Parameters / Attributes:**  
| Name       | Type   | Description                             |
|------------|--------|-----------------------------------------|
| settings   | dict   | A dictionary containing application settings loaded from environment variables. |

**Expected Input:**  
• Environment variables should be properly set before the application is run.  
• Keys in the environment variables should match the expected settings.  
• Values should be of appropriate types as defined by the application logic.

**Returns:**  
`dict` – a dictionary of application settings.

**Detailed Logic:**  
• The `Settings` class initializes by reading environment variables.  
• It maps these variables to specific application settings.  
• If a required environment variable is not set, it may lead to default values being used or exceptions being raised, depending on the implementation.  
• The settings can be accessed as attributes or through dictionary-like access.

**Raises / Errors:**  
• Raises `KeyError` if a required environment variable is missing and no default is provided.  
• Raises `ValueError` if an environment variable is set but contains an invalid value.

**Usage Example:**  
```python
import os

# Set environment variables before running the application
os.environ['APP_SETTING_1'] = 'value1'
os.environ['APP_SETTING_2'] = 'value2'

# Access settings
settings = Settings()
print(settings['APP_SETTING_1'])  # Outputs: value1
```