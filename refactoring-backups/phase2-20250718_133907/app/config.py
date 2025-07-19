from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Dynamic English Course Creator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database settings - Use environment variable with fallback
    DATABASE_URL: str = "sqlite:///./data/development.db"  # Default fallback for development
    
    # Database connection pool settings (for PostgreSQL)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # Database SSL settings (for production)
    DB_SSL_MODE: Optional[str] = None  # "require", "verify-ca", "verify-full"
    DB_SSL_CERT: Optional[str] = None
    DB_SSL_KEY: Optional[str] = None
    DB_SSL_CA: Optional[str] = None
    
    # JWT settings
    JWT_SECRET_KEY: str = "PFXaKWj/FHCm3NH44Tl+rwKjheAE0UXMwk6TPGOCR7d5bR8Si85t6crxuUvlgc+iQdTF1ajuA+JPrNHAMd1vWA=="
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis settings (optional for development)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # AWS settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    
    # Email settings
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Security settings
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def cors_origins_list(self) -> list:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    API_KEY_HEADER: str = "X-API-Key"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # AI/LLM API Keys (optional)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Production settings
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    @property
    def database_ssl_config(self) -> dict:
        """Get SSL configuration for database connection"""
        if not self.is_production or not self.DB_SSL_MODE:
            return {}
        
        ssl_config = {"sslmode": self.DB_SSL_MODE}
        
        if self.DB_SSL_CERT:
            ssl_config["sslcert"] = self.DB_SSL_CERT
        if self.DB_SSL_KEY:
            ssl_config["sslkey"] = self.DB_SSL_KEY
        if self.DB_SSL_CA:
            ssl_config["sslrootcert"] = self.DB_SSL_CA
            
        return ssl_config
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

# Create settings instance
settings = Settings() 