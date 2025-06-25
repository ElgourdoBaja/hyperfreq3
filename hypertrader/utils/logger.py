"""
Logging configuration
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logging(level: str = "INFO", log_to_file: bool = True, log_dir: str = None):
    """Setup application logging"""
    
    # Create log directory if needed
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / "data" / "logs"
    else:
        log_dir = Path(log_dir)
        
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    if log_to_file:
        # File handler for general logs
        log_file = log_dir / f"hypertrader_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Separate handler for errors
        error_log_file = log_dir / f"hypertrader_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
        
        # Trading activity log
        trading_log_file = log_dir / f"trading_{datetime.now().strftime('%Y%m%d')}.log"
        trading_handler = logging.handlers.RotatingFileHandler(
            trading_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        trading_handler.setLevel(logging.INFO)
        trading_handler.setFormatter(formatter)
        
        # Create trading logger
        trading_logger = logging.getLogger('trading')
        trading_logger.addHandler(trading_handler)
        trading_logger.setLevel(logging.INFO)
        trading_logger.propagate = False  # Don't propagate to root logger
    
    logging.info("Logging system initialized")

def get_trading_logger():
    """Get the trading activity logger"""
    return logging.getLogger('trading')

def get_error_logger():
    """Get the error logger"""
    return logging.getLogger('error')

class TradeLogger:
    """Specialized logger for trading activities"""
    
    def __init__(self):
        self.logger = get_trading_logger()
        
    def log_order_placed(self, order_data: dict):
        """Log order placement"""
        self.logger.info(f"ORDER_PLACED: {order_data}")
        
    def log_order_filled(self, order_data: dict):
        """Log order fill"""
        self.logger.info(f"ORDER_FILLED: {order_data}")
        
    def log_order_cancelled(self, order_id: str, reason: str = ""):
        """Log order cancellation"""
        self.logger.info(f"ORDER_CANCELLED: {order_id} - {reason}")
        
    def log_position_opened(self, position_data: dict):
        """Log position opening"""
        self.logger.info(f"POSITION_OPENED: {position_data}")
        
    def log_position_closed(self, position_data: dict, pnl: float):
        """Log position closing"""
        self.logger.info(f"POSITION_CLOSED: {position_data} - PnL: {pnl}")
        
    def log_strategy_signal(self, strategy_name: str, signal_data: dict):
        """Log strategy signal"""
        self.logger.info(f"STRATEGY_SIGNAL: {strategy_name} - {signal_data}")
        
    def log_api_error(self, error: str, context: str = ""):
        """Log API error"""
        self.logger.error(f"API_ERROR: {context} - {error}")
        
    def log_balance_update(self, balance_data: dict):
        """Log balance update"""
        self.logger.info(f"BALANCE_UPDATE: {balance_data}")