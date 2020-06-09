"""Configuration module."""
from .loader import SettingsLoader, SETTINGS_ENV


settings = SettingsLoader()  # pylint: disable=invalid-name
