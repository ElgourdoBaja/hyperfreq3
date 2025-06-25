"""
Application settings and configuration management
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class AppSettings:
    """Application settings manager"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent.parent / "data" / "settings.json"
        self.logger = logging.getLogger(__name__)
        self._settings = self._load_default_settings()
        self.load()
        
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            # Application settings
            "app_version": "1.5.0",
            "first_run": True,
            "logging_level": "INFO",
            "auto_save": True,
            "auto_save_interval": 300,  # seconds
            
            # UI settings
            "ui": {
                "theme": "dark",
                "window_width": 1200,
                "window_height": 800,
                "window_maximized": False,
                "show_notifications": True,
                "sound_enabled": True,
                "refresh_interval": 5000,  # milliseconds
            },
            
            # Trading settings
            "trading": {
                "default_order_size": 0.1,
                "default_leverage": 1,
                "risk_limit_percent": 2.0,
                "auto_cancel_orders": False,
                "confirm_orders": True,
            },
            
            # Data settings
            "data": {
                "store_trade_history": True,
                "max_history_days": 30,
                "cache_market_data": True,
                "backup_enabled": True,
            },
            
            # API settings (will be set through UI)
            "api": {
                "hyperliquid": {
                    "wallet_address": "",
                    "api_key": "",
                    "api_secret": "",
                    "environment": "mainnet",  # mainnet or testnet
                    "timeout": 30,
                    "retry_attempts": 3,
                }
            },
            
            # Advanced settings
            "advanced": {
                "debug_mode": False,
                "developer_mode": False,
                "api_rate_limit": 10,  # requests per second
                "websocket_reconnect": True,
            }
        }
        
    def load(self):
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults (preserving new default settings)
                    self._merge_settings(self._settings, saved_settings)
                    self.logger.info("Settings loaded successfully")
            else:
                self.logger.info("No settings file found, using defaults")
                # Create the directory if it doesn't exist
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                self.save()
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            
    def _merge_settings(self, default: Dict, saved: Dict):
        """Recursively merge saved settings with defaults"""
        for key, value in saved.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_settings(default[key], value)
                else:
                    default[key] = value
                    
    def save(self):
        """Save settings to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
            self.logger.info("Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'ui.theme')"""
        try:
            keys = key.split('.')
            value = self._settings
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any):
        """Set a setting value using dot notation"""
        try:
            keys = key.split('.')
            setting = self._settings
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in setting:
                    setting[k] = {}
                setting = setting[k]
                
            # Set the value
            setting[keys[-1]] = value
            
            # Auto-save if enabled
            if self.get('auto_save', True):
                self.save()
                
        except Exception as e:
            self.logger.error(f"Failed to set setting {key}: {e}")
            
    def get_api_credentials(self) -> Dict[str, str]:
        """Get API credentials for Hyperliquid"""
        return {
            "wallet_address": self.get("api.hyperliquid.wallet_address", ""),
            "api_key": self.get("api.hyperliquid.api_key", ""),
            "api_secret": self.get("api.hyperliquid.api_secret", ""),
            "environment": self.get("api.hyperliquid.environment", "mainnet"),
        }
        
    def set_api_credentials(self, wallet_address: str, api_key: str, api_secret: str, environment: str = "mainnet"):
        """Set API credentials for Hyperliquid"""
        self.set("api.hyperliquid.wallet_address", wallet_address)
        self.set("api.hyperliquid.api_key", api_key)
        self.set("api.hyperliquid.api_secret", api_secret)
        self.set("api.hyperliquid.environment", environment)
        
    def is_api_configured(self) -> bool:
        """Check if API credentials are configured"""
        creds = self.get_api_credentials()
        return all([
            creds["wallet_address"],
            creds["api_key"], 
            creds["api_secret"]
        ])
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self._settings = self._load_default_settings()
        self.save()
        
    def export_settings(self, file_path: str):
        """Export settings to a file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
            self.logger.info(f"Settings exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            
    def import_settings(self, file_path: str):
        """Import settings from a file"""
        try:
            with open(file_path, 'r') as f:
                imported_settings = json.load(f)
                self._merge_settings(self._settings, imported_settings)
                self.save()
            self.logger.info(f"Settings imported from {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")