"""
Configuration management module.

Loads and manages application configuration from TOML/YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Try to import TOML, fallback to YAML
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Python < 3.11
    except ImportError:
        tomllib = None

try:
    import yaml
except ImportError:
    yaml = None


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional path to config directory. Defaults to project root/config.
        """
        # Load environment variables
        load_dotenv()

        # Set config directory
        if config_path:
            self.config_dir = Path(config_path)
        else:
            self.config_dir = Path(__file__).parent.parent.parent / "config"

        # Load configuration files (try TOML first, then YAML)
        self.app_config = self._load_config("config.toml", "config.yaml")
        try:
            self.model_config = self._load_config("model_config.toml", "model_config.yaml")
        except:
            self.model_config = {}

    def _load_config(self, toml_filename: str, yaml_filename: str) -> Dict[str, Any]:
        """
        Load configuration file (TOML preferred, YAML fallback).

        Args:
            toml_filename: Name of the TOML file to try first.
            yaml_filename: Name of the YAML file as fallback.

        Returns:
            Dictionary containing configuration values.
        """
        # Try TOML first
        toml_path = self.config_dir.parent / toml_filename
        if toml_path.exists() and tomllib:
            try:
                with open(toml_path, "rb") as f:
                    config = tomllib.load(f)
                return self._replace_env_vars(config)
            except Exception:
                pass  # Fall back to YAML
        
        # Try YAML fallback
        yaml_path = self.config_dir / yaml_filename
        if yaml_path.exists() and yaml:
            try:
                with open(yaml_path, "r") as f:
                    config = yaml.safe_load(f)
                return self._replace_env_vars(config)
            except Exception:
                pass
        
        # If neither exists, return empty dict (don't crash)
        return {}

    def _replace_env_vars(self, config: Any) -> Any:
        """
        Recursively replace environment variable placeholders in config.

        Args:
            config: Configuration dictionary or value.

        Returns:
            Configuration with environment variables replaced.
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Handle ${VAR:default} format
            if config.startswith("${") and config.endswith("}"):
                var_expr = config[2:-1]
                if ":" in var_expr:
                    var_name, default = var_expr.split(":", 1)
                    return os.getenv(var_name.strip(), default.strip())
                else:
                    var_name = var_expr.strip()
                    value = os.getenv(var_name)
                    if value is None:
                        # Return empty string for optional variables (like Pinecone)
                        # Only raise error for critical variables
                        if var_name in ["DATABASE_URL", "ALPHA_VANTAGE_API_KEY"]:
                            raise ValueError(f"Environment variable {var_name} not set")
                        return ""  # Return empty string for optional variables
                    return value
            return config
        else:
            return config

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.

        Args:
            key_path: Dot-separated path to configuration value (e.g., 'api.port').
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        keys = key_path.split(".")
        value = self.app_config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(f"Configuration key not found: {key_path}")

    def get_model_config(self, key_path: str, default: Any = None) -> Any:
        """
        Get model configuration value by dot-separated key path.

        Args:
            key_path: Dot-separated path to configuration value.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        keys = key_path.split(".")
        value = self.model_config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(f"Model configuration key not found: {key_path}")


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Global Config instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

