"""
Position models
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class Position:
    """Trading position"""
    coin: str
    size: float
    entry_price: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    side: 'OrderSide' = None  # Will be imported from order module
    leverage: float = 1.0
    margin_used: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
            
    @property
    def market_value(self) -> float:
        """Current market value of the position"""
        return self.size * self.current_price
        
    @property
    def cost_basis(self) -> float:
        """Cost basis of the position"""
        return self.size * self.entry_price
        
    @property
    def pnl_percentage(self) -> float:
        """PnL as percentage of cost basis"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100
        
    @property
    def price_change_percentage(self) -> float:
        """Price change percentage since entry"""
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100
        
    def update_current_price(self, price: float):
        """Update current price and recalculate PnL"""
        self.current_price = price
        self._calculate_unrealized_pnl()
        self.updated_at = datetime.utcnow()
        
    def _calculate_unrealized_pnl(self):
        """Calculate unrealized PnL based on current price"""
        price_diff = self.current_price - self.entry_price
        
        # Import here to avoid circular imports
        from .order import OrderSide
        
        if self.side == OrderSide.LONG:
            self.unrealized_pnl = self.size * price_diff
        elif self.side == OrderSide.SHORT:
            self.unrealized_pnl = self.size * -price_diff
        else:
            self.unrealized_pnl = 0.0
            
    def is_profitable(self) -> bool:
        """Check if position is currently profitable"""
        return self.unrealized_pnl > 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "coin": self.coin,
            "size": self.size,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "side": self.side.value if self.side else None,
            "leverage": self.leverage,
            "margin_used": self.margin_used,
            "market_value": self.market_value,
            "cost_basis": self.cost_basis,
            "pnl_percentage": self.pnl_percentage,
            "price_change_percentage": self.price_change_percentage,
            "is_profitable": self.is_profitable(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """Create from dictionary"""
        from .order import OrderSide
        
        return cls(
            coin=data["coin"],
            size=data["size"],
            entry_price=data["entry_price"],
            current_price=data.get("current_price", 0.0),
            unrealized_pnl=data.get("unrealized_pnl", 0.0),
            realized_pnl=data.get("realized_pnl", 0.0),
            side=OrderSide(data["side"]) if data.get("side") else None,
            leverage=data.get("leverage", 1.0),
            margin_used=data.get("margin_used", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )