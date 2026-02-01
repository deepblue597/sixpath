"""
Configuration management for the application.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database type: 'sqlite' or 'postgresql'
    db_type: str = "postgresql"
    
    # SQLite settings
    sqlite_db_path: str = "./data/sixpath.db"
    
    # PostgreSQL settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sixpath"
    db_user: str = "sixpath_user"
    db_password: str = "sixpath_password"
    
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # JWT settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    

    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database_url(self) -> str:
        """Construct database URL based on db_type."""
        if self.db_type.lower() == "sqlite":
            return f"sqlite:///{self.sqlite_db_path}"
        else:  # postgresql
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() # type: ignore
