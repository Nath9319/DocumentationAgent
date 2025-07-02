from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    APP_NAME: str = "Scientific Calculator API"
    API_V1_STR: str = "/api/v1"

    class Config:
        # This allows pydantic to look for a .env file for environment variables
        env_file = ".env"

# Instantiate settings to be used throughout the application
settings = Settings()
