from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    cors_allowed_origins: str = "*"
    rate_limit: str = "60/minute"

    model_config = {"env_file": ".env"}


settings = Settings()
