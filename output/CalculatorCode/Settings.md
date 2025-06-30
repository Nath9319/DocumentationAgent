# Documentation for `Settings`

```python
class Settings:
    """
    Application settings, loaded from environment variables.

    This class is responsible for managing the configuration settings 
    of the application. It retrieves values from the environment, allowing 
    for flexible configuration without hardcoding values in the source code. 
    This approach enhances security and adaptability, especially in 
    different deployment environments.

    Attributes:
        - (str) DATABASE_URL: The URL for the database connection.
        - (str) SECRET_KEY: A secret key used for cryptographic operations.
        - (str) DEBUG: A flag indicating whether the application is in debug mode.
    """

    # Class implementation goes here
```

### Documentation Breakdown:

- **Class Name:** `Settings`
- **Category:** Class
- **File Path:** `Calculator\app\core\config.py`
- **Lines:** 3 to 12
- **Purpose:** To manage application settings loaded from environment variables.
- **Key Features:**
  - Retrieves configuration values from the environment.
  - Supports flexible and secure application configuration.
- **Attributes (Examples):**
  - `DATABASE_URL`: Connection string for the database.
  - `SECRET_KEY`: Key for cryptographic functions.
  - `DEBUG`: Boolean flag for enabling debug mode.

This documentation provides a clear overview of the `Settings` class, its purpose, and its attributes, making it easier for developers to understand and utilize the class effectively.