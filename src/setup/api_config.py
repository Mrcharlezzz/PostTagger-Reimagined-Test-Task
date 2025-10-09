from pydantic_settings import BaseSettings

class ApiSettings(BaseSettings):
    MAX_DIGITS: int = 2000
    CORS_ALLOW_ALL: bool = True

    class Config:
        env_file = ".env"

def get_api_settings() -> ApiSettings:
    return ApiSettings()

#REMOVE CORS_ALLOW_ALL