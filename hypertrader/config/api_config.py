"""
API configuration and management
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class HyperliquidConfig:
    """Hyperliquid API configuration"""
    wallet_address: str = ""
    api_key: str = ""
    api_secret: str = ""
    environment: str = "mainnet"  # mainnet or testnet
    timeout: int = 30
    retry_attempts: int = 3
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the current environment"""
        if self.environment == "testnet":
            return "https://api.hyperliquid-testnet.xyz"
        else:
            return "https://api.hyperliquid.xyz"
            
    @property
    def ws_url(self) -> str:
        """Get the WebSocket URL for the current environment"""
        if self.environment == "testnet":
            return "wss://api.hyperliquid-testnet.xyz/ws"
        else:
            return "wss://api.hyperliquid.xyz/ws"
            
    def is_configured(self) -> bool:
        """Check if all required credentials are set"""
        return bool(self.wallet_address and self.api_key and self.api_secret)
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "wallet_address": self.wallet_address,
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "environment": self.environment,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'HyperliquidConfig':
        """Create from dictionary"""
        return cls(
            wallet_address=data.get("wallet_address", ""),
            api_key=data.get("api_key", ""),
            api_secret=data.get("api_secret", ""),
            environment=data.get("environment", "mainnet"),
            timeout=data.get("timeout", 30),
            retry_attempts=data.get("retry_attempts", 3),
        )

class APIConfigManager:
    """Manages API configurations for different exchanges"""
    
    def __init__(self):
        self.hyperliquid = HyperliquidConfig()
        
    def load_from_settings(self, settings: Dict):
        """Load configuration from settings dictionary"""
        if "api" in settings and "hyperliquid" in settings["api"]:
            self.hyperliquid = HyperliquidConfig.from_dict(settings["api"]["hyperliquid"])
            
    def save_to_settings(self) -> Dict:
        """Save configuration to settings dictionary format"""
        return {
            "api": {
                "hyperliquid": self.hyperliquid.to_dict()
            }
        }
        
    def test_connection(self, exchange: str = "hyperliquid") -> bool:
        """Test API connection"""
        if exchange == "hyperliquid":
            return self._test_hyperliquid_connection()
        return False
        
    def _test_hyperliquid_connection(self) -> bool:
        """Test Hyperliquid API connection"""
        try:
            if not self.hyperliquid.is_configured():
                return False
                
            # Import here to avoid circular imports
            from core.hyperliquid_client import HyperliquidClient
            
            client = HyperliquidClient(self.hyperliquid)
            return client.test_connection()
            
        except Exception as e:
            print(f"Hyperliquid connection test failed: {e}")
            return False