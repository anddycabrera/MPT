from functools import lru_cache
from pydantic import BaseSettings
class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM Demo"
    API_V1_STR: str = "/api/v1"
    
    OPENAI_API_KEY: str
    SERPAPI_API_KEY: str
    BROKER_URL: str    
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
settings = get_settings()