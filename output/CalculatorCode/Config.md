# Documentation for `Config`

```python
class Config:
    """
    A class to manage application configuration settings.

    Attributes:
        env_file (str): The name of the environment file to load configuration variables from. 
                        Default is '.env'.
    """
    env_file = '.env'
``` 

### Documentation Overview

#### Class: `Config`

The `Config` class is designed to encapsulate configuration settings for the application. It primarily holds the name of the environment file from which configuration variables can be loaded.

#### Attributes

- **`env_file` (str)**: This attribute specifies the name of the environment file that contains configuration variables. The default value is set to `'.env'`.

### Usage

To use the `Config` class, you can access the `env_file` attribute to determine the configuration file being used:

```python
config = Config()
print(config.env_file)  # Output: '.env'
```

This class serves as a foundational component for managing application settings and can be extended or modified as needed to accommodate additional configuration requirements.