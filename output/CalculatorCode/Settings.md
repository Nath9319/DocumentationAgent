# Documentation for `Settings`

```python
class Settings(BaseSettings):
    """
    A class to manage application settings, loaded from environment variables.

    This class inherits from `BaseSettings` and is designed to encapsulate
    the configuration settings for the application. The settings are primarily
    loaded from environment variables, allowing for flexible configuration
    across different environments.

    Attributes:
        APP_NAME (str): The name of the application. Default is 'Scientific Calculator API'.
        API_V1_STR (str): The base path for the API version 1. Default is '/api/v1'.

    Configuration:
        The class uses a nested `Config` class to specify additional settings.
        The `env_file` attribute indicates that environment variables should
        be loaded from a file named '.env'.

    Example:
        To access the settings, you can create an instance of the Settings class:
        
        ```python
        settings = Settings()
        print(settings.APP_NAME)  # Outputs: Scientific Calculator API
        ```

    Note:
        Ensure that the required environment variables are defined in the
        specified `.env` file for the application to function correctly.
    """
    APP_NAME: str = 'Scientific Calculator API'
    API_V1_STR: str = '/api/v1'

    class Config:
        env_file = '.env'
``` 

### Key Points:
- The docstring provides a clear overview of the class purpose, attributes, and usage.
- It includes an example to demonstrate how to instantiate the class and access its attributes.
- Important notes about environment variables and configuration are highlighted for clarity.