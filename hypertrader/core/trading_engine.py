"""
Trading engine for order management and execution
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime

from core.hyperliquid_client import HyperliquidClient
from core.data_manager import DataManager
from models.order import Order, OrderType, OrderSide, OrderStatus
from models.strategy import Strategy, StrategyStatus
from utils.helpers import calculate_position_size, validate_order_params

class TradingEngine:
    """Trading engine for automated order management"""
    
    def __init__(self, hyperliquid_client: HyperliquidClient, data_manager: DataManager):
        self.hyperliquid_client = hyperliquid_client
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
        # Engine state
        self.is_running = False
        self.engine_thread = None
        
        # Order tracking
        self.active_orders: Dict[str, Order] = {}
        self.order_callbacks: Dict[str, Callable] = {}
        
        # Strategy management
        self.active_strategies: Dict[str, Strategy] = {}
        
        # Risk management
        self.daily_loss_limit = 1000.0  # USD
        self.max_position_size = 10.0   # USD
        self.current_daily_loss = 0.0
        
    def start(self):
        """Start the trading engine"""
        if self.is_running:
            return
            
        self.is_running = True
        self.engine_thread = threading.Thread(target=self._engine_loop)
        self.engine_thread.daemon = True
        self.engine_thread.start()
        
        self.logger.info("Trading engine started")
        
    def stop(self):
        """Stop the trading engine"""
        self.is_running = False
        if self.engine_thread:
            self.engine_thread.join(timeout=5)
            
        self.logger.info("Trading engine stopped")
        
    def place_order(self, coin: str, side: OrderSide, size: float, price: Optional[float] = None,
                   order_type: OrderType = OrderType.LIMIT, callback: Optional[Callable] = None) -> Optional[Order]:
        """Place an order through the engine"""
        try:
            # Validate order parameters
            validation = validate_order_params(coin, size, price)
            if not validation["valid"]:
                self.logger.error(f"Order validation failed: {validation['errors']}")
                return None
                
            # Risk checks
            if not self._check_risk_limits(size, price):
                self.logger.error("Order rejected by risk management")
                return None
                
            # Place order via API
            order = self.hyperliquid_client.place_order(coin, side, size, price, order_type)
            
            if order:
                # Track the order
                self.active_orders[order.order_id] = order
                
                # Set callback if provided
                if callback:
                    self.order_callbacks[order.order_id] = callback
                    
                # Save to database
                self.data_manager.save_order(order)
                
                self.logger.info(f"Order placed: {order.order_id}")
                
            return order
            
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return None
            
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if order_id not in self.active_orders:
                self.logger.warning(f"Order {order_id} not found in active orders")
                return False
                
            order = self.active_orders[order_id]
            
            # Cancel via API
            success = self.hyperliquid_client.cancel_order(order.coin, order_id)
            
            if success:
                # Update order status
                order.cancel()
                self.data_manager.save_order(order)
                
                # Remove from active orders
                del self.active_orders[order_id]
                if order_id in self.order_callbacks:
                    del self.order_callbacks[order_id]
                    
                self.logger.info(f"Order cancelled: {order_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to cancel order: {e}")
            return False
            
    def add_strategy(self, strategy: Strategy):
        """Add a strategy to the engine"""
        try:
            self.active_strategies[strategy.strategy_id] = strategy
            self.data_manager.save_strategy(strategy)
            self.logger.info(f"Strategy added: {strategy.name}")
        except Exception as e:
            self.logger.error(f"Failed to add strategy: {e}")
            
    def remove_strategy(self, strategy_id: str):
        """Remove a strategy from the engine"""
        try:
            if strategy_id in self.active_strategies:
                del self.active_strategies[strategy_id]
                self.logger.info(f"Strategy removed: {strategy_id}")
        except Exception as e:
            self.logger.error(f"Failed to remove strategy: {e}")
            
    def start_strategy(self, strategy_id: str):
        """Start a specific strategy"""
        try:
            if strategy_id in self.active_strategies:
                strategy = self.active_strategies[strategy_id]
                strategy.start()
                self.data_manager.save_strategy(strategy)
                self.logger.info(f"Strategy started: {strategy.name}")
        except Exception as e:
            self.logger.error(f"Failed to start strategy: {e}")
            
    def stop_strategy(self, strategy_id: str):
        """Stop a specific strategy"""
        try:
            if strategy_id in self.active_strategies:
                strategy = self.active_strategies[strategy_id]
                strategy.stop()
                self.data_manager.save_strategy(strategy)
                self.logger.info(f"Strategy stopped: {strategy.name}")
        except Exception as e:
            self.logger.error(f"Failed to stop strategy: {e}")
            
    def get_active_orders(self) -> List[Order]:
        """Get all active orders"""
        return list(self.active_orders.values())
        
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Get status of a specific order"""
        if order_id in self.active_orders:
            return self.active_orders[order_id].status
        return None
        
    def _engine_loop(self):
        """Main engine loop"""
        while self.is_running:
            try:
                # Update order statuses
                self._update_orders()
                
                # Process strategies
                self._process_strategies()
                
                # Risk management checks
                self._check_risk_management()
                
                # Sleep before next iteration
                time.sleep(1)  # 1 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in engine loop: {e}")
                time.sleep(5)  # Longer sleep on error
                
    def _update_orders(self):
        """Update status of active orders"""
        try:
            # Get current open orders from API
            api_orders = self.hyperliquid_client.get_open_orders()
            api_order_ids = {order.order_id for order in api_orders}
            
            # Check for filled/cancelled orders
            orders_to_remove = []
            
            for order_id, order in self.active_orders.items():
                if order_id not in api_order_ids:
                    # Order no longer open - likely filled or cancelled
                    if order.status == OrderStatus.PENDING:
                        order.status = OrderStatus.FILLED  # Assume filled for now
                        
                    # Save updated order
                    self.data_manager.save_order(order)
                    
                    # Execute callback if exists
                    if order_id in self.order_callbacks:
                        try:
                            self.order_callbacks[order_id](order)
                        except Exception as e:
                            self.logger.error(f"Error in order callback: {e}")
                            
                    orders_to_remove.append(order_id)
                    
            # Remove completed orders
            for order_id in orders_to_remove:
                del self.active_orders[order_id]
                if order_id in self.order_callbacks:
                    del self.order_callbacks[order_id]
                    
        except Exception as e:
            self.logger.error(f"Error updating orders: {e}")
            
    def _process_strategies(self):
        """Process active strategies"""
        try:
            for strategy in self.active_strategies.values():
                if strategy.status == StrategyStatus.ACTIVE:
                    # This is where strategy logic would be implemented
                    # For now, just update the last signal time
                    pass
        except Exception as e:
            self.logger.error(f"Error processing strategies: {e}")
            
    def _check_risk_management(self):
        """Check risk management rules"""
        try:
            # Check daily loss limit
            if self.current_daily_loss >= self.daily_loss_limit:
                self.logger.warning("Daily loss limit reached - stopping all strategies")
                for strategy in self.active_strategies.values():
                    if strategy.status == StrategyStatus.ACTIVE:
                        strategy.pause()
                        
        except Exception as e:
            self.logger.error(f"Error in risk management: {e}")
            
    def _check_risk_limits(self, size: float, price: Optional[float]) -> bool:
        """Check if order passes risk limits"""
        try:
            # Calculate position value
            if price is None:
                # For market orders, get current price
                return True  # Skip risk check for market orders for now
                
            position_value = size * price
            
            # Check maximum position size
            if position_value > self.max_position_size:
                self.logger.warning(f"Position value {position_value} exceeds max position size {self.max_position_size}")
                return False
                
            # Check daily loss limit
            if self.current_daily_loss >= self.daily_loss_limit:
                self.logger.warning("Daily loss limit reached")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            return False
            
    def get_engine_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            "is_running": self.is_running,
            "active_orders": len(self.active_orders),
            "active_strategies": len([s for s in self.active_strategies.values() if s.status == StrategyStatus.ACTIVE]),
            "total_strategies": len(self.active_strategies),
            "current_daily_loss": self.current_daily_loss,
            "daily_loss_limit": self.daily_loss_limit
        }