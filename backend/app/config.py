from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    agnes_api_key: str = ""
    log_level: str = "INFO"

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
