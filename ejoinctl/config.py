"""Configuration management for ejoinctl."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def parse_host_port(host_spec: str, default_port: int = 80) -> tuple[str, int]:
    """Parse host specification that may include port.
    
    Args:
        host_spec: Host specification like "192.168.1.100" or "192.168.1.100:8080"
        default_port: Default port to use if not specified in host_spec
        
    Returns:
        Tuple of (host, port)
        
    Raises:
        ValueError: If port is invalid (not a number or out of range)
        
    Examples:
        >>> parse_host_port("192.168.1.100")
        ('192.168.1.100', 80)
        >>> parse_host_port("13.228.130.204:60140")
        ('13.228.130.204', 60140)
    """
    if ':' in host_spec:
        host_part, port_part = host_spec.split(':', 1)
        try:
            port = int(port_part)
            if port < 1 or port > 65535:
                raise ValueError(f"Port {port} is out of valid range (1-65535)")
            return host_part, port
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Invalid port '{port_part}' - must be a number")
            raise
    return host_spec, default_port


@dataclass
class EjoinConfig:
    """Configuration for EJOIN device connection and settings."""
    
    host: str
    port: int = 80
    username: str = "root"
    password: str = ""
    
    # HTTP client settings
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    max_retries: int = 3
    
    # Database settings
    db_path: Path = field(default_factory=lambda: Path("./ejoinctl.db"))
    
    # Webhook receiver settings
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8080
    
    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "EjoinConfig":
        """Load configuration from environment variables and .env file."""
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from common locations
            for env_path in [Path(".env"), Path.home() / ".ejoinctl.env"]:
                if env_path.exists():
                    load_dotenv(env_path)
                    break
        
        # Get required host
        host = os.getenv("EJOIN_HOST")
        if not host:
            raise ValueError(
                "EJOIN_HOST environment variable is required. "
                "Set it in your environment or .env file."
            )
        
        # Parse host:port format if provided
        host_part, port = parse_host_port(host, int(os.getenv("EJOIN_PORT", "80")))
        
        return cls(
            host=host_part,
            port=port,
            username=os.getenv("EJOIN_USER", "root"),
            password=os.getenv("EJOIN_PASS", ""),
            connect_timeout=float(os.getenv("EJOIN_CONNECT_TIMEOUT", "10.0")),
            read_timeout=float(os.getenv("EJOIN_READ_TIMEOUT", "30.0")),
            db_path=Path(os.getenv("EJOIN_DB_PATH", "./ejoinctl.db")),
            webhook_host=os.getenv("EJOIN_WEBHOOK_HOST", "0.0.0.0"),
            webhook_port=int(os.getenv("EJOIN_WEBHOOK_PORT", "8080")),
        )
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the EJOIN device."""
        # Handle case where host already includes port
        if ':' in self.host:
            return f"http://{self.host}"
        return f"http://{self.host}:{self.port}"
    
    def auth_params(self) -> dict[str, str]:
        """Get authentication parameters for API requests."""
        return {
            "username": self.username,
            "password": self.password,
        }


class ConfigManager:
    """Manages configuration profiles and current settings."""
    
    def __init__(self):
        self._current_config: Optional[EjoinConfig] = None
        self._profiles: dict[str, EjoinConfig] = {}
    
    def get_config(self, profile: Optional[str] = None) -> EjoinConfig:
        """Get configuration, optionally by profile name."""
        if profile and profile in self._profiles:
            return self._profiles[profile]
        
        if self._current_config is None:
            self._current_config = EjoinConfig.from_env()
        
        return self._current_config
    
    def add_profile(self, name: str, config: EjoinConfig) -> None:
        """Add a named configuration profile."""
        self._profiles[name] = config
    
    def list_profiles(self) -> list[str]:
        """List available configuration profiles."""
        return list(self._profiles.keys())


# Global configuration manager instance
config_manager = ConfigManager()