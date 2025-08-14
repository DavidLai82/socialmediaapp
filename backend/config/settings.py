"""
Application configuration and settings management
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="socialmediaai", env="DB_NAME")
    user: str = Field(default="socialmedia_user", env="DB_USER")
    password: str = Field(default="password", env="DB_PASSWORD")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    socket_timeout: int = Field(default=30, env="REDIS_SOCKET_TIMEOUT")
    socket_connect_timeout: int = Field(default=30, env="REDIS_CONNECT_TIMEOUT")
    
    @property
    def url(self) -> str:
        """Get Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class AIServiceSettings(BaseSettings):
    """AI service configuration settings."""
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_timeout: int = Field(default=60, env="OPENAI_TIMEOUT")
    
    # Anthropic settings
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=2000, env="ANTHROPIC_MAX_TOKENS")
    anthropic_timeout: int = Field(default=60, env="ANTHROPIC_TIMEOUT")
    
    # CrewAI settings
    crewai_api_key: Optional[str] = Field(default=None, env="CREW_AI_API_KEY")
    max_agents: int = Field(default=5, env="MAX_AGENTS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")
    task_retry_attempts: int = Field(default=3, env="TASK_RETRY_ATTEMPTS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class SocialMediaSettings(BaseSettings):
    """Social media API configuration settings."""
    
    # Twitter/X settings
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN_SECRET")
    twitter_bearer_token: Optional[str] = Field(default=None, env="TWITTER_BEARER_TOKEN")
    
    # LinkedIn settings
    linkedin_client_id: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_SECRET")
    
    # Instagram settings
    instagram_access_token: Optional[str] = Field(default=None, env="INSTAGRAM_ACCESS_TOKEN")
    instagram_client_id: Optional[str] = Field(default=None, env="INSTAGRAM_CLIENT_ID")
    instagram_client_secret: Optional[str] = Field(default=None, env="INSTAGRAM_CLIENT_SECRET")
    
    # Facebook settings
    facebook_app_id: Optional[str] = Field(default=None, env="FACEBOOK_APP_ID")
    facebook_app_secret: Optional[str] = Field(default=None, env="FACEBOOK_APP_SECRET")
    facebook_access_token: Optional[str] = Field(default=None, env="FACEBOOK_ACCESS_TOKEN")
    
    # TikTok settings
    tiktok_client_key: Optional[str] = Field(default=None, env="TIKTOK_CLIENT_KEY")
    tiktok_client_secret: Optional[str] = Field(default=None, env="TIKTOK_CLIENT_SECRET")
    
    # YouTube settings
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    youtube_client_id: Optional[str] = Field(default=None, env="YOUTUBE_CLIENT_ID")
    youtube_client_secret: Optional[str] = Field(default=None, env="YOUTUBE_CLIENT_SECRET")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Password settings
    min_password_length: int = Field(default=8, env="MIN_PASSWORD_LENGTH")
    max_password_length: int = Field(default=128, env="MAX_PASSWORD_LENGTH")
    require_special_chars: bool = Field(default=True, env="REQUIRE_SPECIAL_CHARS")
    require_numbers: bool = Field(default=True, env="REQUIRE_NUMBERS")
    require_uppercase: bool = Field(default=True, env="REQUIRE_UPPERCASE")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=200, env="RATE_LIMIT_BURST")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ServerSettings(BaseSettings):
    """Server configuration settings."""
    
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="info", env="LOG_LEVEL")
    workers: int = Field(default=1, env="WORKERS")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods: List[str] = Field(default=["*"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('cors_methods', pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(',')]
        return v
    
    @validator('cors_headers', pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class FileStorageSettings(BaseSettings):
    """File storage configuration settings."""
    
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi"],
        env="ALLOWED_EXTENSIONS"
    )
    
    @validator('allowed_extensions', pre=True)
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    log_max_size: int = Field(default=10485760, env="LOG_MAX_SIZE")  # 10MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_date_format: str = Field(default="%Y-%m-%d %H:%M:%S", env="LOG_DATE_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class MonitoringSettings(BaseSettings):
    """Monitoring and metrics configuration settings."""
    
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    
    # Performance thresholds
    cpu_warning_threshold: float = Field(default=70.0, env="CPU_WARNING_THRESHOLD")
    cpu_critical_threshold: float = Field(default=90.0, env="CPU_CRITICAL_THRESHOLD")
    memory_warning_threshold: float = Field(default=80.0, env="MEMORY_WARNING_THRESHOLD")
    memory_critical_threshold: float = Field(default=95.0, env="MEMORY_CRITICAL_THRESHOLD")
    disk_warning_threshold: float = Field(default=85.0, env="DISK_WARNING_THRESHOLD")
    disk_critical_threshold: float = Field(default=95.0, env="DISK_CRITICAL_THRESHOLD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ApplicationSettings(BaseSettings):
    """Main application configuration settings."""
    
    # Application metadata
    app_name: str = Field(default="Social Media AI Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_description: str = Field(
        default="Multi-agent AI platform for social media optimization",
        env="APP_DESCRIPTION"
    )
    environment: str = Field(default="development", env="ENVIRONMENT")
    api_version: str = Field(default="v1", env="API_VERSION")
    
    # Feature flags
    enable_websockets: bool = Field(default=True, env="ENABLE_WEBSOCKETS")
    enable_background_tasks: bool = Field(default=True, env="ENABLE_BACKGROUND_TASKS")
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    ai_services: AIServiceSettings = AIServiceSettings()
    social_media: SocialMediaSettings = SocialMediaSettings()
    security: SecuritySettings = SecuritySettings()
    server: ServerSettings = ServerSettings()
    file_storage: FileStorageSettings = FileStorageSettings()
    logging: LoggingSettings = LoggingSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_environments = ['development', 'staging', 'production', 'testing']
        if v.lower() not in valid_environments:
            raise ValueError(f'Environment must be one of {valid_environments}')
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == 'development'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == 'production'
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == 'testing'
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = ApplicationSettings()


def get_settings() -> ApplicationSettings:
    """Get application settings instance."""
    return settings


def validate_required_settings():
    """Validate that all required settings are properly configured."""
    
    errors = []
    
    # Check required security settings
    if not settings.security.secret_key:
        errors.append("SECRET_KEY is required")
    
    if not settings.security.jwt_secret_key:
        errors.append("JWT_SECRET_KEY is required")
    
    # Check AI service settings
    if not settings.ai_services.openai_api_key and not settings.ai_services.anthropic_api_key:
        errors.append("At least one AI service API key (OpenAI or Anthropic) is required")
    
    # Check database settings
    if not settings.database.user or not settings.database.password:
        errors.append("Database credentials (DB_USER and DB_PASSWORD) are required")
    
    # Production-specific validations
    if settings.is_production:
        if settings.server.debug:
            errors.append("DEBUG mode should be disabled in production")
        
        if settings.server.reload:
            errors.append("RELOAD should be disabled in production")
        
        if "localhost" in settings.server.cors_origins:
            errors.append("Localhost should not be in CORS origins for production")
    
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))


def setup_logging():
    """Set up application logging configuration."""
    
    import logging
    import logging.handlers
    import os
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.logging.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.server.log_level.upper()),
        format=settings.logging.log_format,
        datefmt=settings.logging.log_date_format,
        handlers=[
            logging.StreamHandler(),  # Console handler
            logging.handlers.RotatingFileHandler(
                settings.logging.log_file,
                maxBytes=settings.logging.log_max_size,
                backupCount=settings.logging.log_backup_count
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def print_startup_info():
    """Print application startup information."""
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         Social Media AI Platform                              ║
║                                Version {settings.app_version:<8}                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Environment: {settings.environment:<15} │ Debug: {str(settings.server.debug):<15}    ║
║ Host: {settings.server.host:<20} │ Port: {settings.server.port:<16}   ║
║ Database: {settings.database.host}:{settings.database.port:<13} │ Redis: {settings.redis.host}:{settings.redis.port:<14} ║
║ Log Level: {settings.server.log_level.upper():<14} │ Workers: {settings.server.workers:<15} ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)


# Export commonly used settings for easy access
__all__ = [
    'settings',
    'get_settings',
    'validate_required_settings',
    'setup_logging',
    'print_startup_info',
    'ApplicationSettings',
    'DatabaseSettings',
    'RedisSettings',
    'AIServiceSettings',
    'SocialMediaSettings',
    'SecuritySettings',
    'ServerSettings',
    'FileStorageSettings',
    'LoggingSettings',
    'MonitoringSettings'
]