"""
Configuration management for MQTT API Backend Service

This module handles configuration loading from environment variables
and provides default values for all service settings.
"""

import os
from typing import Optional

class Config:
    """Configuration class for MQTT API Backend Service"""
    
    # MQTT Broker Configuration
    MQTT_BROKER_HOST: str = os.getenv('MQTT_BROKER_HOST', 'localhost')
    MQTT_BROKER_PORT: int = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    MQTT_USERNAME: str = os.getenv('MQTT_USERNAME', 'api')
    MQTT_PASSWORD: str = os.getenv('MQTT_PASSWORD', 'api_password')
    MQTT_KEEPALIVE: int = int(os.getenv('MQTT_KEEPALIVE', '60'))
    MQTT_CLEAN_SESSION: bool = os.getenv('MQTT_CLEAN_SESSION', 'true').lower() == 'true'
    
    # API Server Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_WORKERS: int = int(os.getenv('API_WORKERS', '1'))
    API_RELOAD: bool = os.getenv('API_RELOAD', 'false').lower() == 'true'
    
    # Message Storage Configuration
    MAX_HISTORY_SIZE: int = int(os.getenv('MAX_HISTORY_SIZE', '1000'))
    MESSAGE_RETENTION_HOURS: int = int(os.getenv('MESSAGE_RETENTION_HOURS', '24'))
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv('WS_HEARTBEAT_INTERVAL', '30'))
    WS_MAX_CONNECTIONS: int = int(os.getenv('WS_MAX_CONNECTIONS', '100'))
    
    # Security Configuration
    CORS_ORIGINS: list = os.getenv('CORS_ORIGINS', '*').split(',')
    API_KEY_REQUIRED: bool = os.getenv('API_KEY_REQUIRED', 'false').lower() == 'true'
    API_KEY: Optional[str] = os.getenv('API_KEY')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv('HEALTH_CHECK_TIMEOUT', '10'))
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW: int = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration values"""
        try:
            # Validate MQTT configuration
            assert cls.MQTT_BROKER_PORT > 0 and cls.MQTT_BROKER_PORT <= 65535
            assert cls.MQTT_KEEPALIVE > 0
            assert cls.MQTT_USERNAME and cls.MQTT_PASSWORD
            
            # Validate API configuration
            assert cls.API_PORT > 0 and cls.API_PORT <= 65535
            assert cls.API_WORKERS > 0
            assert cls.MAX_HISTORY_SIZE > 0
            assert cls.MESSAGE_RETENTION_HOURS > 0
            
            # Validate WebSocket configuration
            assert cls.WS_HEARTBEAT_INTERVAL > 0
            assert cls.WS_MAX_CONNECTIONS > 0
            
            # Validate security configuration
            if cls.API_KEY_REQUIRED:
                assert cls.API_KEY is not None and len(cls.API_KEY) > 0
            
            # Validate rate limiting configuration
            assert cls.RATE_LIMIT_REQUESTS > 0
            assert cls.RATE_LIMIT_WINDOW > 0
            
            return True
            
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary"""
        return {
            'mqtt_broker_host': cls.MQTT_BROKER_HOST,
            'mqtt_broker_port': cls.MQTT_BROKER_PORT,
            'mqtt_username': cls.MQTT_USERNAME,
            'mqtt_keepalive': cls.MQTT_KEEPALIVE,
            'mqtt_clean_session': cls.MQTT_CLEAN_SESSION,
            'api_host': cls.API_HOST,
            'api_port': cls.API_PORT,
            'api_workers': cls.API_WORKERS,
            'max_history_size': cls.MAX_HISTORY_SIZE,
            'message_retention_hours': cls.MESSAGE_RETENTION_HOURS,
            'ws_heartbeat_interval': cls.WS_HEARTBEAT_INTERVAL,
            'ws_max_connections': cls.WS_MAX_CONNECTIONS,
            'cors_origins': cls.CORS_ORIGINS,
            'api_key_required': cls.API_KEY_REQUIRED,
            'log_level': cls.LOG_LEVEL,
            'health_check_interval': cls.HEALTH_CHECK_INTERVAL,
            'health_check_timeout': cls.HEALTH_CHECK_TIMEOUT,
            'rate_limit_enabled': cls.RATE_LIMIT_ENABLED,
            'rate_limit_requests': cls.RATE_LIMIT_REQUESTS,
            'rate_limit_window': cls.RATE_LIMIT_WINDOW
        }

# Global configuration instance
config = Config()

# Validate configuration on import
if not config.validate():
    raise ValueError("Invalid configuration detected")
