"""
Utility helper functions
"""

import re
import time
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import logging

def format_currency(amount: float, currency: str = "USD", decimal_places: int = 2) -> str:
    """Format currency amount with proper formatting"""
    try:
        if currency == "USD":
            symbol = "$"
        else:
            symbol = currency + " "
            
        if amount >= 1000000:
            return f"{symbol}{amount/1000000:.{decimal_places-1}f}M"
        elif amount >= 1000:
            return f"{symbol}{amount/1000:.{decimal_places-1}f}K"
        else:
            return f"{symbol}{amount:.{decimal_places}f}"
    except:
        return f"${0:.{decimal_places}f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format percentage with proper sign"""
    try:
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.{decimal_places}f}%"
    except:
        return "0.00%"

def format_number(value: float, decimal_places: int = 4) -> str:
    """Format number with proper decimal places"""
    try:
        return f"{value:.{decimal_places}f}"
    except:
        return "0.0000"

def validate_wallet_address(address: str) -> bool:
    """Validate Ethereum wallet address format"""
    if not address:
        return False
    
    # Check if it starts with 0x and has correct length
    pattern = r'^0x[a-fA-F0-9]{40}$'
    return bool(re.match(pattern, address))

def validate_private_key(private_key: str) -> bool:
    """Validate private key format"""
    if not private_key:
        return False
    
    # Remove 0x prefix if present
    if private_key.startswith('0x'):
        private_key = private_key[2:]
    
    # Check if it's 64 hex characters
    pattern = r'^[a-fA-F0-9]{64}$'
    return bool(re.match(pattern, private_key))

def handle_api_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """Handle API errors and return formatted error info"""
    logger = logging.getLogger(__name__)
    
    error_info = {
        "success": False,
        "error": str(error),
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the error
    logger.error(f"API Error in {context}: {error}")
    
    return error_info

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def get_time_ago(timestamp: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
        
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def calculate_position_size(account_balance: float, risk_percent: float, 
                          entry_price: float, stop_loss_price: float) -> float:
    """Calculate position size based on risk management"""
    try:
        if stop_loss_price == 0 or entry_price == 0:
            return 0.0
            
        risk_amount = account_balance * (risk_percent / 100)
        price_diff = abs(entry_price - stop_loss_price)
        
        if price_diff == 0:
            return 0.0
            
        position_size = risk_amount / price_diff
        return position_size
        
    except:
        return 0.0

def validate_order_params(coin: str, size: float, price: Optional[float] = None) -> Dict[str, Any]:
    """Validate order parameters"""
    errors = []
    
    if not coin:
        errors.append("Coin symbol is required")
    
    if size <= 0:
        errors.append("Order size must be greater than 0")
        
    if price is not None and price <= 0:
        errors.append("Price must be greater than 0")
        
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def calculate_pnl(entry_price: float, current_price: float, size: float, 
                 side: str) -> float:
    """Calculate PnL for a position"""
    try:
        price_diff = current_price - entry_price
        
        if side.lower() in ['long', 'buy']:
            return size * price_diff
        elif side.lower() in ['short', 'sell']:
            return size * -price_diff
        else:
            return 0.0
    except:
        return 0.0

def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string"""
    try:
        return timestamp.strftime(format_str)
    except:
        return "Unknown"

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string to datetime"""
    try:
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
                
        return None
    except:
        return None

def debounce(wait_time: float):
    """Decorator to debounce function calls"""
    def decorator(func):
        last_called = [0]
        
        def wrapper(*args, **kwargs):
            now = datetime.utcnow().timestamp()
            if now - last_called[0] >= wait_time:
                last_called[0] = now
                return func(*args, **kwargs)
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator