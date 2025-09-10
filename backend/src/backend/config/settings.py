import os
from dotenv import load_dotenv

# Load .env file from current working directory
load_dotenv(override=True)


class Settings:
    """Application settings."""

    def __init__(self):
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

        # Application
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")

        # Session
        self.session_expire_hours = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))
        
        # Media/File storage
        self.media_dir = os.getenv("MEDIA_DIR", "media")


# Global settings instance
settings = Settings()
