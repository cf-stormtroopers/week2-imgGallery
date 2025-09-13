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
        self.minio_host = os.getenv("MINIO_HOST", "localhost:9010")
        self.minio_root_user = os.getenv("MINIO_ROOT_USER", "minioadmin")
        self.minio_root_password = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
        self.minio_bucket = os.getenv("MINIO_BUCKET", "gallery")

        # Qdrant
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

        # Replicate
        self.replicate_api_key = os.getenv("REPLICATE_API_KEY", "")


# Global settings instance
settings = Settings()
