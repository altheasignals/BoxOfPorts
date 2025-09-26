"""Configuration management for BoxOfPorts."""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

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
        >>> parse_host_port("203.0.113.100:60140")
        ('203.0.113.100', 60140)
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
    device_alias: str = ""

    # HTTP client settings
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    max_retries: int = 3

    # Database settings
    db_path: Path = field(default_factory=lambda: Path("./boxofports.db"))

    # Webhook receiver settings
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8080

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "EjoinConfig":
        """Load configuration from environment variables and .env file."""
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from common locations
            for env_path in [Path(".env"), Path.home() / ".boxofports.env"]:
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
            device_alias=os.getenv("EJOIN_ALIAS", ""),
            connect_timeout=float(os.getenv("EJOIN_CONNECT_TIMEOUT", "10.0")),
            read_timeout=float(os.getenv("EJOIN_READ_TIMEOUT", "30.0")),
            db_path=Path(os.getenv("EJOIN_DB_PATH", "./boxofports.db")),
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

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary for serialization."""
        data = asdict(self)
        # Convert Path objects to strings
        data['db_path'] = str(data['db_path'])
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EjoinConfig":
        """Create config from dictionary."""
        # Convert string paths back to Path objects
        if 'db_path' in data:
            data['db_path'] = Path(data['db_path'])
        # device_alias may be missing in older profiles
        data.setdefault('device_alias', '')
        return cls(**data)


class ConfigManager:
    """Manages configuration profiles and current settings with persistence."""

    def __init__(self):
        self._current_config: EjoinConfig | None = None
        self._profiles: dict[str, EjoinConfig] = {}
        self._config_dir = Path.home() / ".boxofports"
        self._profiles_file = self._config_dir / "profiles.json"
        self._current_profile_file = self._config_dir / "current_profile"
        self._current_profile: str | None = None

        # Ensure config directory exists
        self._config_dir.mkdir(exist_ok=True)

        # Load existing profiles and current profile
        self._load_profiles()
        self._load_current_profile()

    def _load_profiles(self) -> None:
        """Load profiles from disk."""
        if self._profiles_file.exists():
            try:
                with open(self._profiles_file) as f:
                    profiles_data = json.load(f)

                self._profiles = {}
                updated = False
                for name, config_data in profiles_data.items():
                    cfg = EjoinConfig.from_dict(config_data)
                    if not cfg.device_alias:
                        first_word = name.split()[0] if name else ""
                        cfg.device_alias = first_word or cfg.host
                        updated = True
                    self._profiles[name] = cfg

                # Save back to disk if any profile was updated to persist the alias defaults
                if updated:
                    self._save_profiles()

            except Exception as e:
                print(f"Warning: Could not load profiles: {e}")
                self._profiles = {}

    def _save_profiles(self) -> None:
        """Save profiles to disk."""
        try:
            profiles_data = {}
            for name, config in self._profiles.items():
                profiles_data[name] = config.to_dict()

            with open(self._profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save profiles: {e}")

    def _load_current_profile(self) -> None:
        """Load current profile name from disk."""
        if self._current_profile_file.exists():
            try:
                with open(self._current_profile_file) as f:
                    self._current_profile = f.read().strip()
            except Exception:
                self._current_profile = None

    def _save_current_profile(self) -> None:
        """Save current profile name to disk."""
        try:
            if self._current_profile:
                with open(self._current_profile_file, 'w') as f:
                    f.write(self._current_profile)
            elif self._current_profile_file.exists():
                self._current_profile_file.unlink()
        except Exception as e:
            print(f"Warning: Could not save current profile: {e}")

    def get_config(self, profile: str | None = None) -> EjoinConfig:
        """Get configuration, optionally by profile name."""
        # Use specified profile, or current profile, or fallback to env
        target_profile = profile or self._current_profile

        if target_profile and target_profile in self._profiles:
            return self._profiles[target_profile]

        # Fallback to environment-based config
        if self._current_config is None:
            try:
                self._current_config = EjoinConfig.from_env()
            except ValueError:
                # If no env config available and no profiles, create a basic one
                if not self._profiles:
                    raise ValueError(
                        "No configuration available. Either set environment variables "
                        "(EJOIN_HOST, etc.) or create a profile with 'boxofports config add-profile'."
                    )
                # Use the first available profile
                first_profile = next(iter(self._profiles.keys()))
                return self._profiles[first_profile]

        return self._current_config

    def add_profile(self, name: str, config: EjoinConfig) -> None:
        """Add a named configuration profile."""
        self._profiles[name] = config
        self._save_profiles()

    def remove_profile(self, name: str) -> bool:
        """Remove a profile. Returns True if profile existed and was removed."""
        if name in self._profiles:
            del self._profiles[name]
            # If we're removing the current profile, clear it
            if self._current_profile == name:
                self._current_profile = None

            # If only one profile remains, automatically set it as current
            remaining_profiles = list(self._profiles.keys())
            if len(remaining_profiles) == 1 and self._current_profile != remaining_profiles[0]:
                self._current_profile = remaining_profiles[0]

            self._save_current_profile()
            self._save_profiles()
            return True
        return False

    def switch_profile(self, name: str) -> bool:
        """Switch to a different profile. Returns True if profile exists."""
        if name in self._profiles:
            self._current_profile = name
            self._current_config = None  # Clear cached config to reload
            self._save_current_profile()
            return True
        return False

    def get_current_profile(self) -> str | None:
        """Get the name of the current active profile."""
        return self._current_profile

    def list_profiles(self) -> list[str]:
        """List available configuration profiles."""
        return list(self._profiles.keys())

    def get_profile_config(self, name: str) -> EjoinConfig | None:
        """Get configuration for a specific profile."""
        return self._profiles.get(name)


# Global configuration manager instance
config_manager = ConfigManager()
