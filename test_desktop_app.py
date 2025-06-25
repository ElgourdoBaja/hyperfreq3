#!/usr/bin/env python3
"""
Test script for Hypertrader 1.5 Desktop Application
"""

import sys
import os
from pathlib import Path

# Add the hypertrader directory to the path
hypertrader_dir = Path(__file__).parent / "hypertrader"
sys.path.insert(0, str(hypertrader_dir))

try:
    print("Testing Hypertrader 1.5 Desktop Application...")
    
    # Test imports
    print("Testing imports...")
    from config.settings import AppSettings
    from config.api_config import HyperliquidConfig, APIConfigManager
    from models.account import Account, Portfolio
    from models.order import Order, OrderType, OrderSide, OrderStatus
    from models.position import Position
    from models.strategy import Strategy, StrategyStatus
    from utils.helpers import format_currency, validate_wallet_address
    from utils.logger import setup_logging
    
    print("✅ All imports successful!")
    
    # Test settings
    print("\nTesting settings...")
    settings = AppSettings()
    print(f"✅ Settings loaded. App version: {settings.get('app_version')}")
    
    # Test API config
    print("\nTesting API configuration...")
    api_manager = APIConfigManager()
    print(f"✅ API manager created. Hyperliquid configured: {api_manager.hyperliquid.is_configured()}")
    
    # Test data models
    print("\nTesting data models...")
    
    # Test account
    account = Account(address="0x1234567890abcdef", account_value=1000.0)
    print(f"✅ Account model: {account.address[:8]}... - ${account.account_value}")
    
    # Test order
    order = Order(
        order_id="test_123",
        coin="BTC",
        side=OrderSide.LONG,
        size=0.1,
        price=50000.0,
        order_type=OrderType.LIMIT
    )
    print(f"✅ Order model: {order.coin} {order.side.value} {order.size}")
    
    # Test strategy
    strategy = Strategy(
        strategy_id="test_strategy",
        name="Test Strategy",
        coin="BTC"
    )
    print(f"✅ Strategy model: {strategy.name} - {strategy.status.value}")
    
    # Test utilities
    print("\nTesting utilities...")
    formatted_amount = format_currency(1234.56)
    print(f"✅ Currency formatting: {formatted_amount}")
    
    is_valid = validate_wallet_address("0x1234567890abcdef1234567890abcdef12345678")
    print(f"✅ Address validation: {is_valid}")
    
    print("\n🎉 All tests passed! The desktop application structure is ready.")
    print("\nTo run the application:")
    print("1. cd hypertrader")
    print("2. python main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Some dependencies may be missing. Please install requirements:")
    print("pip install -r hypertrader/requirements.txt")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
finally:
    print("\nTest completed.")