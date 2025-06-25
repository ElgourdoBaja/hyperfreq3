"""
Hyperliquid API client for desktop application
"""

import asyncio
import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import websockets

from config.api_config import HyperliquidConfig
from models.account import Account, Portfolio
from models.position import Position
from models.order import Order, OrderType, OrderSide
from utils.helpers import format_currency, handle_api_error

class HyperliquidClient:
    """Hyperliquid API client for trading operations"""
    
    def __init__(self, config: HyperliquidConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = config.timeout
        
        # Initialize Hyperliquid SDK components
        self._init_hyperliquid_sdk()
        
        # WebSocket connection
        self.ws_connection = None
        self.ws_running = False
        self.ws_thread = None
        
        # Data cache
        self.last_update = {}
        self.cache_timeout = 5  # seconds
        
    def _init_hyperliquid_sdk(self):
        """Initialize Hyperliquid Python SDK"""
        try:
            if self.config.is_configured():
                from hyperliquid.info import Info
                from hyperliquid.exchange import Exchange
                
                self.info = Info(self.config.base_url, skip_ws=True)
                self.exchange = Exchange(None, self.config.base_url, wallet=self.config.api_secret)
                
                self.logger.info(f"Hyperliquid SDK initialized for {self.config.environment}")
                self.logger.info(f"Target wallet: {self.config.wallet_address}")
                self.logger.info(f"Exchange wallet: {self.exchange.wallet.address}")
            else:
                self.info = None
                self.exchange = None
                self.logger.warning("Hyperliquid SDK not initialized - missing credentials")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Hyperliquid SDK: {e}")
            self.info = None
            self.exchange = None
            
    def test_connection(self) -> bool:
        """Test connection to Hyperliquid API"""
        try:
            if not self.config.is_configured():
                return False
                
            # Test public API first
            response = requests.get(f"{self.config.base_url}/info", timeout=10)
            if response.status_code != 200:
                return False
                
            # Test user state endpoint
            if self.info:
                user_state = self.info.user_state(self.config.wallet_address)
                return isinstance(user_state, dict)
                
            return False
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
            
    def get_account_info(self) -> Optional[Account]:
        """Get account information"""
        try:
            if not self.info:
                return None
                
            # Check cache
            cache_key = "account_info"
            if self._is_cached(cache_key):
                return self.last_update[cache_key]["data"]
                
            user_state = self.info.user_state(self.config.wallet_address)
            
            if not user_state:
                return None
                
            margin_summary = user_state.get("marginSummary", {})
            
            account = Account(
                address=self.config.wallet_address,
                account_value=float(margin_summary.get("accountValue", 0)),
                available_balance=float(user_state.get("withdrawable", 0)),
                margin_used=float(margin_summary.get("totalMarginUsed", 0)),
                total_pnl=float(margin_summary.get("totalRawUsd", 0)),
                margin_summary=margin_summary,
                cross_margin_summary=user_state.get("crossMarginSummary", {})
            )
            
            # Cache the result
            self._cache_data(cache_key, account)
            
            self.logger.info(f"Account info retrieved: ${account.account_value:.2f}")
            return account
            
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            return None
            
    def get_portfolio(self) -> Optional[Portfolio]:
        """Get portfolio with positions"""
        try:
            if not self.info:
                return None
                
            # Check cache
            cache_key = "portfolio"
            if self._is_cached(cache_key):
                return self.last_update[cache_key]["data"]
                
            user_state = self.info.user_state(self.config.wallet_address)
            
            if not user_state:
                return None
                
            margin_summary = user_state.get("marginSummary", {})
            
            # Create portfolio
            portfolio = Portfolio(
                account_value=float(margin_summary.get("accountValue", 0)),
                available_balance=float(user_state.get("withdrawable", 0)),
                margin_used=float(margin_summary.get("totalMarginUsed", 0)),
                total_pnl=float(margin_summary.get("totalRawUsd", 0)),
                daily_pnl=0.0  # Calculate this separately if needed
            )
            
            # Add positions
            positions = []
            for pos_data in user_state.get("assetPositions", []):
                position_info = pos_data.get("position", {})
                
                if float(position_info.get("szi", 0)) != 0:
                    position = Position(
                        coin=position_info.get("coin", ""),
                        size=abs(float(position_info.get("szi", 0))),
                        entry_price=float(position_info.get("entryPx", 0)),
                        current_price=0.0,  # Will be updated with market data
                        unrealized_pnl=float(position_info.get("unrealizedPnl", 0)),
                        realized_pnl=0.0,  # Not available in this endpoint
                        side=OrderSide.LONG if float(position_info.get("szi", 0)) > 0 else OrderSide.SHORT
                    )
                    positions.append(position)
                    
            portfolio.positions = positions
            
            # Cache the result
            self._cache_data(cache_key, portfolio)
            
            self.logger.info(f"Portfolio retrieved: {len(positions)} positions, ${portfolio.account_value:.2f}")
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Failed to get portfolio: {e}")
            return None
            
    def get_market_data(self, coin: str) -> Optional[Dict]:
        """Get market data for a specific coin"""
        try:
            if not self.info:
                return None
                
            # Check cache
            cache_key = f"market_{coin}"
            if self._is_cached(cache_key, timeout=2):  # Shorter cache for market data
                return self.last_update[cache_key]["data"]
                
            # Get all mids (current prices)
            all_mids = self.info.all_mids()
            
            if coin not in all_mids:
                return None
                
            current_price = float(all_mids[coin])
            
            # Get 24h data (simplified)
            market_data = {
                "coin": coin,
                "price": current_price,
                "bid": current_price * 0.999,  # Approximate
                "ask": current_price * 1.001,  # Approximate
                "volume_24h": 0.0,  # Would need separate API call
                "change_24h": 0.0,  # Would need historical data
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            self._cache_data(cache_key, market_data)
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Failed to get market data for {coin}: {e}")
            return None
            
    def get_order_book(self, coin: str, depth: int = 10) -> Optional[Dict]:
        """Get order book for a coin"""
        try:
            if not self.info:
                return None
                
            l2_book = self.info.l2_snapshot(coin)
            
            if not l2_book:
                return None
                
            levels = l2_book.get("levels", [])
            
            bids = []
            asks = []
            
            for level in levels:
                price = float(level["px"])
                size = float(level["sz"])
                n = level.get("n", 0)
                
                if n > 0:  # Bid
                    bids.append({"price": price, "size": size})
                elif n < 0:  # Ask
                    asks.append({"price": price, "size": size})
                    
            # Sort and limit
            bids = sorted(bids, key=lambda x: x["price"], reverse=True)[:depth]
            asks = sorted(asks, key=lambda x: x["price"])[:depth]
            
            return {
                "coin": coin,
                "bids": bids,
                "asks": asks,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get order book for {coin}: {e}")
            return None
            
    def place_order(self, coin: str, side: OrderSide, size: float, price: Optional[float] = None, 
                   order_type: OrderType = OrderType.LIMIT, reduce_only: bool = False) -> Optional[Order]:
        """Place a trading order"""
        try:
            if not self.exchange:
                self.logger.error("Exchange not initialized")
                return None
                
            # Prepare order request
            is_buy = side == OrderSide.LONG
            
            if order_type == OrderType.MARKET:
                order_request = {
                    "coin": coin,
                    "is_buy": is_buy,
                    "sz": size,
                    "order_type": {"market": {}},
                    "reduce_only": reduce_only
                }
            else:  # LIMIT
                if price is None:
                    raise ValueError("Price required for limit orders")
                    
                order_request = {
                    "coin": coin,
                    "is_buy": is_buy,
                    "sz": size,
                    "limit_px": price,
                    "order_type": {"limit": {"tif": "Gtc"}},  # Good Till Cancelled
                    "reduce_only": reduce_only
                }
                
            response = self.exchange.order(order_request)
            
            if response.get("status") == "ok":
                order_data = response.get("response", {}).get("data", {})
                
                order = Order(
                    order_id=str(order_data.get("oid", "")),
                    coin=coin,
                    side=side,
                    size=size,
                    price=price,
                    order_type=order_type,
                    status="PENDING",
                    filled_size=0.0,
                    remaining_size=size,
                    average_fill_price=0.0,
                    reduce_only=reduce_only,
                    timestamp=datetime.utcnow()
                )
                
                self.logger.info(f"Order placed: {side} {size} {coin} @ {price}")
                return order
            else:
                error_msg = response.get("response", {}).get("error", "Unknown error")
                self.logger.error(f"Order failed: {error_msg}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return None
            
    def cancel_order(self, coin: str, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if not self.exchange:
                return False
                
            response = self.exchange.cancel(coin, int(order_id))
            success = response.get("status") == "ok"
            
            if success:
                self.logger.info(f"Order cancelled: {order_id}")
            else:
                error_msg = response.get("response", {}).get("error", "Unknown error")
                self.logger.error(f"Cancel failed: {error_msg}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to cancel order: {e}")
            return False
            
    def get_open_orders(self) -> List[Order]:
        """Get open orders"""
        try:
            if not self.info:
                return []
                
            open_orders = self.info.open_orders(self.config.wallet_address)
            
            orders = []
            for order_data in open_orders:
                order = Order(
                    order_id=str(order_data.get("oid", "")),
                    coin=order_data.get("coin", ""),
                    side=OrderSide.LONG if order_data.get("side") == "B" else OrderSide.SHORT,
                    size=float(order_data.get("sz", 0)),
                    price=float(order_data.get("limitPx", 0)),
                    order_type=OrderType.LIMIT,  # Assume limit for now
                    status="PENDING",
                    filled_size=0.0,
                    remaining_size=float(order_data.get("sz", 0)),
                    average_fill_price=0.0,
                    reduce_only=order_data.get("reduceOnly", False),
                    timestamp=datetime.utcnow()
                )
                orders.append(order)
                
            return orders
            
        except Exception as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return []
            
    def get_available_coins(self) -> List[str]:
        """Get list of available coins for trading"""
        try:
            if not self.info:
                return []
                
            meta = self.info.meta()
            universe = meta.get("universe", [])
            
            coins = [coin_info["name"] for coin_info in universe]
            return coins
            
        except Exception as e:
            self.logger.error(f"Failed to get available coins: {e}")
            return []
            
    def start_websocket(self, callback=None):
        """Start WebSocket connection for real-time data"""
        if self.ws_running:
            return
            
        self.ws_running = True
        self.ws_thread = threading.Thread(target=self._websocket_worker, args=(callback,))
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
    def stop_websocket(self):
        """Stop WebSocket connection"""
        self.ws_running = False
        if self.ws_thread:
            self.ws_thread.join(timeout=5)
            
    def _websocket_worker(self, callback):
        """WebSocket worker thread"""
        async def websocket_handler():
            try:
                async with websockets.connect(self.config.ws_url) as websocket:
                    self.ws_connection = websocket
                    
                    # Subscribe to relevant channels
                    subscribe_msg = {
                        "method": "subscribe",
                        "subscription": {
                            "type": "allMids"
                        }
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    
                    while self.ws_running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            data = json.loads(message)
                            
                            if callback:
                                callback(data)
                                
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            self.logger.error(f"WebSocket message error: {e}")
                            
            except Exception as e:
                self.logger.error(f"WebSocket connection error: {e}")
                
        # Run the async function
        try:
            asyncio.run(websocket_handler())
        except Exception as e:
            self.logger.error(f"WebSocket worker error: {e}")
            
    def _is_cached(self, key: str, timeout: Optional[int] = None) -> bool:
        """Check if data is cached and not expired"""
        if key not in self.last_update:
            return False
            
        cache_timeout = timeout or self.cache_timeout
        elapsed = time.time() - self.last_update[key]["timestamp"]
        return elapsed < cache_timeout
        
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.last_update[key] = {
            "data": data,
            "timestamp": time.time()
        }
        
    def cleanup(self):
        """Cleanup resources"""
        self.stop_websocket()
        if self.session:
            self.session.close()