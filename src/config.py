"""
Configuration management module
"""

import os
import re
import yaml
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Simple email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


@dataclass
class MonitorConfig:
    """Monitoring configuration"""
    interval_min: int
    interval_max: int
    random_delay_max: int
    run_immediately: bool = True


@dataclass
class OmakaseConfig:
    """omakase.in credentials"""
    email: str
    password: str


@dataclass
class RestaurantConfig:
    """Restaurant configuration"""
    name: str
    slug: str
    url: str
    enabled: bool = True


@dataclass
class GmailConfig:
    """Gmail notification configuration"""
    smtp_server: str
    smtp_port: int
    sender_email: str
    app_password: str
    receiver_email: str


@dataclass
class Config:
    """Main configuration"""
    monitor: MonitorConfig
    omakase: OmakaseConfig
    restaurants: list[RestaurantConfig]
    gmail: GmailConfig


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration from YAML file and environment variables

    Args:
        config_path: Path to config.yaml file

    Returns:
        Config object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    # Load environment variables from .env file
    load_dotenv()

    # Check if config file exists
    if not Path(config_path).exists():
        raise FileNotFoundError(
            f"Configuration file '{config_path}' not found. "
            f"Please copy config.yaml.example to config.yaml and configure it."
        )

    # Load YAML configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML configuration: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to read configuration file: {e}") from e

    # Parse monitor settings
    monitor_data = config_data.get('monitor', {})
    monitor = MonitorConfig(
        interval_min=monitor_data.get('interval_min', 5),
        interval_max=monitor_data.get('interval_max', 10),
        random_delay_max=monitor_data.get('random_delay_max', 120),
        run_immediately=monitor_data.get('run_immediately', True)
    )

    # Parse omakase credentials
    omakase_data = config_data.get('omakase', {})
    omakase = OmakaseConfig(
        email=omakase_data.get('email', ''),
        password=omakase_data.get('password', '')
    )

    # Parse restaurants
    restaurants_data = config_data.get('restaurants', [])
    restaurants = [
        RestaurantConfig(
            name=r.get('name', ''),
            slug=r.get('slug', ''),
            url=r.get('url', ''),
            enabled=r.get('enabled', True)
        )
        for r in restaurants_data
    ]

    # Parse Gmail settings (get app password from environment)
    gmail_data = config_data.get('notification', {}).get('gmail', {})
    gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')

    gmail = GmailConfig(
        smtp_server=gmail_data.get('smtp_server', 'smtp.gmail.com'),
        smtp_port=gmail_data.get('smtp_port', 587),
        sender_email=gmail_data.get('sender_email', ''),
        app_password=gmail_app_password,
        receiver_email=gmail_data.get('receiver_email', '')
    )

    config = Config(
        monitor=monitor,
        omakase=omakase,
        restaurants=restaurants,
        gmail=gmail
    )

    # Validate configuration
    errors = validate_config(config)
    if errors:
        error_msg = "Configuration validation failed:\n  - " + "\n  - ".join(errors)
        raise ValueError(error_msg)

    logger.info(f"Configuration loaded successfully from {config_path}")
    return config


def validate_config(config: Config) -> list[str]:
    """
    Validate configuration and return list of errors

    Args:
        config: Config object to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate monitor settings
    if config.monitor.interval_min < 1:
        errors.append("monitor.interval_min must be at least 1 minute")
    if config.monitor.interval_max < config.monitor.interval_min:
        errors.append("monitor.interval_max must be >= interval_min")
    if config.monitor.random_delay_max < 0:
        errors.append("monitor.random_delay_max must be non-negative")

    # Validate omakase credentials
    if not config.omakase.email:
        errors.append("omakase.email is required")
    elif not EMAIL_REGEX.match(config.omakase.email):
        errors.append("omakase.email is not a valid email address")
    if not config.omakase.password:
        errors.append("omakase.password is required")

    # Validate restaurants
    if not config.restaurants:
        errors.append("At least one restaurant must be configured")

    enabled_restaurants = [r for r in config.restaurants if r.enabled]
    if not enabled_restaurants:
        errors.append("At least one restaurant must be enabled")

    for i, restaurant in enumerate(config.restaurants):
        if not restaurant.name:
            errors.append(f"restaurants[{i}].name is required")
        if not restaurant.slug:
            errors.append(f"restaurants[{i}].slug is required")
        if not restaurant.url:
            errors.append(f"restaurants[{i}].url is required")

    # Validate Gmail settings
    if not config.gmail.sender_email:
        errors.append("notification.gmail.sender_email is required")
    elif not EMAIL_REGEX.match(config.gmail.sender_email):
        errors.append(
            "notification.gmail.sender_email is not a valid email address"
        )

    if not config.gmail.receiver_email:
        errors.append("notification.gmail.receiver_email is required")
    elif not EMAIL_REGEX.match(config.gmail.receiver_email):
        errors.append(
            "notification.gmail.receiver_email is not a valid email address"
        )

    if not config.gmail.app_password:
        errors.append(
            "GMAIL_APP_PASSWORD environment variable is required. "
            "Please set it in your .env file."
        )

    return errors
