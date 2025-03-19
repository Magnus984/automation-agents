from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_title: str = "Automation Agents"
    api_v1_str: str = "/api/v1"
    url: str
    token: str
    openai_api_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()