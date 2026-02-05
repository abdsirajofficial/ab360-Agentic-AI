"""Application configuration"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "ab360"
    debug: bool = False
    log_level: str = "INFO"
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gpt-oss:120b-cloud"  # Default Ollama model
    
    # Database
    database_path: str = "./data/ab360.db"
    vector_store_path: str = "./data/chromadb"
    
    # Performance
    max_response_time: int = 3  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure data directories exist
Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
Path(settings.vector_store_path).mkdir(parents=True, exist_ok=True)
