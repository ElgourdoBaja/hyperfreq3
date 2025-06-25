"""
Strategy models
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class StrategyStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    BACKTESTING = "backtesting"

class StrategyType(Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    SIGNAL_FOLLOWING = "signal_following"

@dataclass
class StrategyConfig:
    """Strategy configuration parameters"""
    # Entry conditions
    entry_signal: str = ""
    entry_price_type: str = "market"  # market, limit, stop
    entry_size_type: str = "fixed"    # fixed, percentage, risk_based
    entry_size_value: float = 0.1
    
    # Exit conditions
    take_profit_enabled: bool = False
    take_profit_percent: float = 5.0
    stop_loss_enabled: bool = False
    stop_loss_percent: float = 2.0
    trailing_stop_enabled: bool = False
    trailing_stop_percent: float = 1.0
    
    # Risk management
    max_position_size: float = 1.0
    max_risk_per_trade: float = 2.0  # percentage of account
    max_drawdown: float = 10.0       # percentage
    daily_loss_limit: float = 5.0    # percentage
    
    # Timing
    max_trade_duration: Optional[int] = None  # minutes
    trading_hours_start: str = "00:00"
    trading_hours_end: str = "23:59"
    
    # Advanced
    leverage: float = 1.0
    hedge_enabled: bool = False
    scale_in_enabled: bool = False
    scale_out_enabled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_signal": self.entry_signal,
            "entry_price_type": self.entry_price_type,
            "entry_size_type": self.entry_size_type,
            "entry_size_value": self.entry_size_value,
            "take_profit_enabled": self.take_profit_enabled,
            "take_profit_percent": self.take_profit_percent,
            "stop_loss_enabled": self.stop_loss_enabled,
            "stop_loss_percent": self.stop_loss_percent,
            "trailing_stop_enabled": self.trailing_stop_enabled,
            "trailing_stop_percent": self.trailing_stop_percent,
            "max_position_size": self.max_position_size,
            "max_risk_per_trade": self.max_risk_per_trade,
            "max_drawdown": self.max_drawdown,
            "daily_loss_limit": self.daily_loss_limit,
            "max_trade_duration": self.max_trade_duration,
            "trading_hours_start": self.trading_hours_start,
            "trading_hours_end": self.trading_hours_end,
            "leverage": self.leverage,
            "hedge_enabled": self.hedge_enabled,
            "scale_in_enabled": self.scale_in_enabled,
            "scale_out_enabled": self.scale_out_enabled
        }

@dataclass
class StrategyPerformance:
    """Strategy performance metrics"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    total_return_percent: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_percent: float = 0.0
    sharpe_ratio: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
        
    @property
    def loss_rate(self) -> float:
        """Calculate loss rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.losing_trades / self.total_trades) * 100
        
    @property
    def avg_trade_pnl(self) -> float:
        """Average PnL per trade"""
        if self.total_trades == 0:
            return 0.0
        return self.total_pnl / self.total_trades
        
    def update_trade(self, pnl: float):
        """Update performance with a new trade"""
        self.total_trades += 1
        self.total_pnl += pnl
        
        if pnl > 0:
            self.winning_trades += 1
            self.avg_win = ((self.avg_win * (self.winning_trades - 1)) + pnl) / self.winning_trades
            if pnl > self.largest_win:
                self.largest_win = pnl
        else:
            self.losing_trades += 1
            self.avg_loss = ((self.avg_loss * (self.losing_trades - 1)) + pnl) / self.losing_trades
            if pnl < self.largest_loss:
                self.largest_loss = pnl
                
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "loss_rate": self.loss_rate,
            "total_pnl": self.total_pnl,
            "avg_trade_pnl": self.avg_trade_pnl,
            "total_return_percent": self.total_return_percent,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_percent": self.max_drawdown_percent,
            "sharpe_ratio": self.sharpe_ratio,
            "profit_factor": self.profit_factor,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "largest_win": self.largest_win,
            "largest_loss": self.largest_loss,
            "consecutive_wins": self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }

@dataclass
class Strategy:
    """Trading strategy"""
    strategy_id: str
    name: str
    description: str = ""
    coin: str = ""
    strategy_type: StrategyType = StrategyType.MANUAL
    status: StrategyStatus = StrategyStatus.STOPPED
    config: StrategyConfig = field(default_factory=StrategyConfig)
    performance: StrategyPerformance = field(default_factory=StrategyPerformance)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_signal_at: Optional[datetime] = None
    
    def start(self):
        """Start the strategy"""
        self.status = StrategyStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        if self.performance.start_date is None:
            self.performance.start_date = datetime.utcnow()
            
    def pause(self):
        """Pause the strategy"""
        self.status = StrategyStatus.PAUSED
        self.updated_at = datetime.utcnow()
        
    def stop(self):
        """Stop the strategy"""
        self.status = StrategyStatus.STOPPED
        self.updated_at = datetime.utcnow()
        self.performance.end_date = datetime.utcnow()
        
    def is_active(self) -> bool:
        """Check if strategy is currently active"""
        return self.status == StrategyStatus.ACTIVE
        
    def is_paused(self) -> bool:
        """Check if strategy is paused"""
        return self.status == StrategyStatus.PAUSED
        
    def is_stopped(self) -> bool:
        """Check if strategy is stopped"""
        return self.status == StrategyStatus.STOPPED
        
    def record_trade(self, pnl: float):
        """Record a trade result"""
        self.performance.update_trade(pnl)
        self.updated_at = datetime.utcnow()
        
    def record_signal(self):
        """Record when a signal was generated"""
        self.last_signal_at = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "coin": self.coin,
            "strategy_type": self.strategy_type.value,
            "status": self.status.value,
            "config": self.config.to_dict(),
            "performance": self.performance.to_dict(),
            "is_active": self.is_active(),
            "is_paused": self.is_paused(),
            "is_stopped": self.is_stopped(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_signal_at": self.last_signal_at.isoformat() if self.last_signal_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Strategy':
        """Create from dictionary"""
        config_data = data.get("config", {})
        config = StrategyConfig(**config_data)
        
        performance_data = data.get("performance", {})
        performance = StrategyPerformance(**performance_data)
        
        return cls(
            strategy_id=data["strategy_id"],
            name=data["name"],
            description=data.get("description", ""),
            coin=data.get("coin", ""),
            strategy_type=StrategyType(data.get("strategy_type", "manual")),
            status=StrategyStatus(data.get("status", "stopped")),
            config=config,
            performance=performance,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_signal_at=datetime.fromisoformat(data["last_signal_at"]) if data.get("last_signal_at") else None
        )