from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/peoplehub"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "peoplehub"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # Application Configuration
    APP_NAME: str = "PeopleHub HRMS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:8501"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()