from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # General Configuration
    PROJECT_NAME: str = "FastAPI IoT API"
    API_V1_STR: str = "/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
