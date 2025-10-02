"""Application configuration and settings."""

import os
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Load .env from project root
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, use system env vars only
    pass


@dataclass
class SMTPSettings:
    """SMTP configuration for email sending."""

    server: str = "smtp.gmail.com"
    port: int = 587
    username: str = ""
    password: str = ""
    use_tls: bool = True


@dataclass
class DatabaseSettings:
    """Database configuration."""

    user: str = "app"
    password: str = "secret"
    name: str = "appdb"
    host: str = "db"
    port: int = 5432

    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class AppSettings:
    """Main application settings."""

    # Application
    app_name: str = "Simple Auth API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security
    bcrypt_rounds: int = 12
    activation_code_expiry_minutes: int = 15

    # Email
    use_mock_email: bool = True
    smtp_settings: SMTPSettings | None = None

    # Database
    database_settings: DatabaseSettings | None = None

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Create settings from environment variables."""

        # SMTP settings if not using mock
        smtp_settings = None
        if not cls._get_bool_env("USE_MOCK_EMAIL", True):
            smtp_settings = SMTPSettings(
                server=os.getenv("SMTP_HOST", "smtp.gmail.com"),
                port=int(os.getenv("SMTP_PORT", "587")),
                username=os.getenv("SMTP_USERNAME", ""),
                password=os.getenv("SMTP_PASSWORD", ""),
                use_tls=cls._get_bool_env("SMTP_USE_TLS", True),
            )

        # Database settings
        database_settings = DatabaseSettings(
            user=os.getenv("DB_USER", "app"),
            password=os.getenv("DB_PASS", "secret"),
            name=os.getenv("DB_NAME", "appdb"),
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "5432")),
        )

        return cls(
            app_name=os.getenv("APP_NAME", "Simple Auth API"),
            app_version=os.getenv("APP_VERSION", "1.0.0"),
            debug=cls._get_bool_env("DEBUG", False),
            bcrypt_rounds=int(os.getenv("BCRYPT_ROUNDS", "12")),
            activation_code_expiry_minutes=int(os.getenv("ACTIVATION_CODE_EXPIRY_MINUTES", "15")),
            use_mock_email=cls._get_bool_env("USE_MOCK_EMAIL", True),
            smtp_settings=smtp_settings,
            database_settings=database_settings,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            reload=cls._get_bool_env("RELOAD", True),
        )

    @staticmethod
    def _get_bool_env(key: str, default: bool) -> bool:
        """Get boolean value from environment."""
        value: str = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")


class SettingsManager:
    """Singleton manager for application settings."""

    _instance: AppSettings | None = None

    @classmethod
    def get_settings(cls) -> AppSettings:
        """Get application settings (singleton)."""
        if cls._instance is None:
            cls._instance = AppSettings.from_env()
        return cls._instance

    @classmethod
    def reset_settings(cls) -> None:
        """Reset settings (useful for testing)."""
        cls._instance = None


def get_settings() -> AppSettings:
    """Get application settings (singleton)."""
    return SettingsManager.get_settings()


def reset_settings() -> None:
    """Reset settings (useful for testing)."""
    SettingsManager.reset_settings()
