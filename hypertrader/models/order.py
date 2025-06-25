"""
Order models and enums
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    LONG = "long"
    SHORT = "short"
    BUY = "buy"   # Alias for LONG
    SELL = "sell" # Alias for SHORT

class OrderStatus(Enum):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TimeInForce(Enum):
    GTC = "gtc"  # Good Till Cancelled
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill
    DAY = "day"  # Day order

@dataclass
class Order:
    """Trading order"""
    order_id: str
    coin: str
    side: OrderSide
    size: float
    price: Optional[float] = None
    order_type: OrderType = OrderType.LIMIT
    status: OrderStatus = OrderStatus.PENDING
    filled_size: float = 0.0
    remaining_size: float = 0.0
    average_fill_price: float = 0.0
    time_in_force: TimeInForce = TimeInForce.GTC
    reduce_only: bool = False
    leverage: float = 1.0
    stop_price: Optional[float] = None
    timestamp: datetime = None
    filled_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.remaining_size == 0.0:
            self.remaining_size = self.size
            
    @property
    def fill_percentage(self) -> float:
        """Percentage of order filled"""
        if self.size == 0:
            return 0.0
        return (self.filled_size / self.size) * 100
        
    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled"""
        return self.status == OrderStatus.FILLED
        
    @property
    def is_partially_filled(self) -> bool:
        """Check if order is partially filled"""
        return self.status == OrderStatus.PARTIALLY_FILLED
        
    @property
    def is_active(self) -> bool:
        """Check if order is still active"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
        
    @property
    def is_buy_order(self) -> bool:
        """Check if this is a buy order"""
        return self.side in [OrderSide.LONG, OrderSide.BUY]
        
    @property
    def is_sell_order(self) -> bool:
        """Check if this is a sell order"""
        return self.side in [OrderSide.SHORT, OrderSide.SELL]
        
    @property
    def total_value(self) -> float:
        """Total value of the order"""
        if self.price is None:
            return 0.0
        return self.size * self.price
        
    @property
    def filled_value(self) -> float:
        """Value of filled portion"""
        if self.average_fill_price == 0.0:
            return 0.0
        return self.filled_size * self.average_fill_price
        
    def update_fill(self, filled_size: float, fill_price: float):
        """Update order with fill information"""
        old_filled_value = self.filled_size * self.average_fill_price
        new_filled_size = self.filled_size + filled_size
        new_filled_value = old_filled_value + (filled_size * fill_price)
        
        self.filled_size = new_filled_size
        self.remaining_size = max(0.0, self.size - self.filled_size)
        
        # Update average fill price
        if new_filled_size > 0:
            self.average_fill_price = new_filled_value / new_filled_size
            
        # Update status
        if self.remaining_size == 0:
            self.status = OrderStatus.FILLED
            self.filled_at = datetime.utcnow()
        elif self.filled_size > 0:
            self.status = OrderStatus.PARTIALLY_FILLED
            
    def cancel(self):
        """Mark order as cancelled"""
        if self.is_active:
            self.status = OrderStatus.CANCELLED
            
    def reject(self, reason: str = ""):
        """Mark order as rejected"""
        self.status = OrderStatus.REJECTED
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "order_id": self.order_id,
            "coin": self.coin,
            "side": self.side.value,
            "size": self.size,
            "price": self.price,
            "order_type": self.order_type.value,
            "status": self.status.value,
            "filled_size": self.filled_size,
            "remaining_size": self.remaining_size,
            "average_fill_price": self.average_fill_price,
            "time_in_force": self.time_in_force.value,
            "reduce_only": self.reduce_only,
            "leverage": self.leverage,
            "stop_price": self.stop_price,
            "fill_percentage": self.fill_percentage,
            "total_value": self.total_value,
            "filled_value": self.filled_value,
            "is_filled": self.is_filled,
            "is_partially_filled": self.is_partially_filled,
            "is_active": self.is_active,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Create from dictionary"""
        return cls(
            order_id=data["order_id"],
            coin=data["coin"],
            side=OrderSide(data["side"]),
            size=data["size"],
            price=data.get("price"),
            order_type=OrderType(data["order_type"]),
            status=OrderStatus(data["status"]),
            filled_size=data.get("filled_size", 0.0),
            remaining_size=data.get("remaining_size", 0.0),
            average_fill_price=data.get("average_fill_price", 0.0),
            time_in_force=TimeInForce(data.get("time_in_force", "gtc")),
            reduce_only=data.get("reduce_only", False),
            leverage=data.get("leverage", 1.0),
            stop_price=data.get("stop_price"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            filled_at=datetime.fromisoformat(data["filled_at"]) if data.get("filled_at") else None
        )