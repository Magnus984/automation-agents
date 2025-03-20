from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_TITLE: str = "Automation Agents"
    API_V1_STR: str = "/api/v1"
    URL: str
    OPENAI_API_KEY: str
    HUGGING_FACE_API_TOKEN: str
    GITHUB_USERNAME: str
    GITHUB_TOKEN: str
    SERPAPI_KEY: str
    RAPIDAPI_KEY: str
    RAPIDAPI_HOST: str
    LEAD_ENRICHMENT_KEY: str
    GROQ_API_KEY: str
    SMTP_SERVER: str
    SMTP_PORT: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    GOOGLE_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()