from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class TimeInForce(str, Enum):
    GTC = "Gtc"  # Good Till Cancelled
    IOC = "Ioc"  # Immediate or Cancel
    FOK = "Fok"  # Fill or Kill

class StrategyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

# Portfolio Models
class Position(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coin: str
    size: float
    entry_price: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    side: OrderSide
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Portfolio(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_value: float = 0.0
    available_balance: float = 0.0
    margin_used: float = 0.0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    positions: List[Position] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Trading Models
class OrderRequest(BaseModel):
    coin: str
    is_buy: bool
    sz: float  # Size
    limit_px: Optional[float] = None  # Price for limit orders
    order_type: OrderType
    time_in_force: TimeInForce = TimeInForce.GTC
    reduce_only: bool = False

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    oid: Optional[int] = None  # Hyperliquid order ID
    coin: str
    side: OrderSide
    size: float
    price: Optional[float] = None
    order_type: OrderType
    status: OrderStatus
    filled_size: float = 0.0
    remaining_size: float = 0.0
    average_fill_price: float = 0.0
    time_in_force: TimeInForce = TimeInForce.GTC
    reduce_only: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Trade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    coin: str
    side: OrderSide
    size: float
    price: float
    fee: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Strategy Models
class StrategyConfig(BaseModel):
    entry_conditions: Dict[str, Any] = {}
    exit_conditions: Dict[str, Any] = {}
    risk_management: Dict[str, Any] = {}
    position_sizing: Dict[str, Any] = {}

class Strategy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    coin: str
    status: StrategyStatus = StrategyStatus.ACTIVE
    config: StrategyConfig
    performance: Dict[str, float] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Market Data Models
class MarketData(BaseModel):
    coin: str
    price: float
    bid: float
    ask: float
    volume_24h: float = 0.0
    change_24h: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CandlestickData(BaseModel):
    coin: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

class OrderBookLevel(BaseModel):
    price: float
    size: float

class OrderBook(BaseModel):
    coin: str
    bids: List[OrderBookLevel] = []
    asks: List[OrderBookLevel] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Account Models
class Account(BaseModel):
    address: str
    account_value: float = 0.0
    margin_summary: Dict[str, float] = {}
    cross_margin_summary: Dict[str, float] = {}
    withdrawable: float = 0.0

# Settings Models
class APICredentials(BaseModel):
    wallet_address: Optional[str] = None  # Main wallet address (public key)
    private_key: Optional[str] = None     # API wallet private key
    environment: str = "testnet"          # testnet or mainnet
    is_configured: bool = False

class UserSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_credentials: APICredentials = APICredentials()
    trading_preferences: Dict[str, Any] = {}
    ui_preferences: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel):
    success: bool
    data: List[Any]
    total: int
    page: int
    page_size: int
    has_more: bool
