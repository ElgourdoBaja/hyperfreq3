"""
Account and portfolio models
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
from .position import Position

@dataclass
class Account:
    """User account information"""
    address: str
    account_value: float = 0.0
    available_balance: float = 0.0
    margin_used: float = 0.0
    total_pnl: float = 0.0
    margin_summary: Dict[str, Any] = field(default_factory=dict)
    cross_margin_summary: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def margin_ratio(self) -> float:
        """Calculate margin utilization ratio"""
        if self.account_value == 0:
            return 0.0
        return self.margin_used / self.account_value
        
    @property
    def free_margin(self) -> float:
        """Calculate free margin available"""
        return max(0.0, self.account_value - self.margin_used)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "address": self.address,
            "account_value": self.account_value,
            "available_balance": self.available_balance,
            "margin_used": self.margin_used,
            "total_pnl": self.total_pnl,
            "margin_ratio": self.margin_ratio,
            "free_margin": self.free_margin,
            "margin_summary": self.margin_summary,
            "cross_margin_summary": self.cross_margin_summary,
            "last_updated": self.last_updated.isoformat()
        }

@dataclass
class Portfolio:
    """Portfolio containing positions and account information"""
    account_value: float = 0.0
    available_balance: float = 0.0
    margin_used: float = 0.0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    positions: List[Position] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def position_count(self) -> int:
        """Number of open positions"""
        return len(self.positions)
        
    @property
    def total_unrealized_pnl(self) -> float:
        """Total unrealized PnL from all positions"""
        return sum(pos.unrealized_pnl for pos in self.positions)
        
    @property
    def total_realized_pnl(self) -> float:
        """Total realized PnL from all positions"""
        return sum(pos.realized_pnl for pos in self.positions)
        
    @property
    def long_positions(self) -> List[Position]:
        """Get all long positions"""
        from .order import OrderSide
        return [pos for pos in self.positions if pos.side == OrderSide.LONG]
        
    @property
    def short_positions(self) -> List[Position]:
        """Get all short positions"""
        from .order import OrderSide
        return [pos for pos in self.positions if pos.side == OrderSide.SHORT]
        
    def get_position(self, coin: str) -> Position:
        """Get position for a specific coin"""
        for pos in self.positions:
            if pos.coin == coin:
                return pos
        return None
        
    def add_position(self, position: Position):
        """Add or update a position"""
        existing = self.get_position(position.coin)
        if existing:
            # Update existing position
            self.positions.remove(existing)
            
        self.positions.append(position)
        self.last_updated = datetime.utcnow()
        
    def remove_position(self, coin: str):
        """Remove a position"""
        self.positions = [pos for pos in self.positions if pos.coin != coin]
        self.last_updated = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "account_value": self.account_value,
            "available_balance": self.available_balance,
            "margin_used": self.margin_used,
            "total_pnl": self.total_pnl,
            "daily_pnl": self.daily_pnl,
            "position_count": self.position_count,
            "total_unrealized_pnl": self.total_unrealized_pnl,
            "total_realized_pnl": self.total_realized_pnl,
            "positions": [pos.to_dict() for pos in self.positions],
            "last_updated": self.last_updated.isoformat()
        }