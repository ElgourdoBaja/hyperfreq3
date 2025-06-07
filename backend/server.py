from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import motor.motor_asyncio
import os
from dotenv import load_dotenv
import json
import asyncio
import websockets
from typing import List, Dict, Optional, Any
from datetime import datetime

# Load environment variables
load_dotenv()

# Import models and services
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import (
    Portfolio, Position, Order, Trade, MarketData, CandlestickData, 
    OrderBook, Account, Strategy, UserSettings, APICredentials,
    OrderRequest, APIResponse, OrderType, OrderSide, OrderStatus
)
from hyperliquid_service import hyperliquid_service

app = FastAPI(title="Hypertrader 1.5 API", version="1.5.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.hypertrader

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.market_data_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Helper functions
async def get_user_settings() -> UserSettings:
    """Get user settings from database"""
    settings_data = await db.user_settings.find_one({})
    if settings_data:
        settings_data.pop("_id", None)
        return UserSettings(**settings_data)
    else:
        # Create default settings
        default_settings = UserSettings()
        await db.user_settings.insert_one(default_settings.dict())
        return default_settings

async def initialize_hyperliquid_service():
    """Initialize Hyperliquid service with credentials from database"""
    try:
        settings = await get_user_settings()
        if settings.api_credentials.wallet_address and settings.api_credentials.api_key and settings.api_credentials.api_secret:
            print("Initializing Hyperliquid service with saved credentials...")
            global hyperliquid_service
            from hyperliquid_service import HyperliquidService
            hyperliquid_service = HyperliquidService(
                wallet_address=settings.api_credentials.wallet_address,
                api_key=settings.api_credentials.api_key,
                api_secret=settings.api_credentials.api_secret,
                environment=settings.api_credentials.environment
            )
            print(f"Hyperliquid service initialized. Configured: {hyperliquid_service.is_configured}")
        else:
            print("No saved credentials found. Using unconfigured service.")
    except Exception as e:
        print(f"Failed to initialize Hyperliquid service with saved credentials: {e}")

# Initialize service with saved credentials on startup
@app.on_event("startup")
async def startup_event():
    await initialize_hyperliquid_service()

# Root endpoint
@app.get("/api/")
async def root():
    return {"message": "Hypertrader 1.5 API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Portfolio endpoints
@app.get("/api/portfolio", response_model=APIResponse)
async def get_portfolio():
    """Get user portfolio with positions and account value"""
    try:
        portfolio = await hyperliquid_service.get_portfolio()
        return APIResponse(
            success=True,
            message="Portfolio retrieved successfully",
            data=portfolio.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account", response_model=APIResponse)
async def get_account_info():
    """Get account information"""
    try:
        account = await hyperliquid_service.get_account_info()
        return APIResponse(
            success=True,
            message="Account info retrieved successfully",
            data=account.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Market data endpoints
@app.get("/api/market/{coin}", response_model=APIResponse)
async def get_market_data(coin: str):
    """Get current market data for a coin"""
    try:
        market_data = await hyperliquid_service.get_market_data(coin.upper())
        return APIResponse(
            success=True,
            message="Market data retrieved successfully",
            data=market_data.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candlesticks/{coin}", response_model=APIResponse)
async def get_candlestick_data(coin: str, interval: str = "1h", limit: int = 100):
    """Get candlestick data for a coin"""
    try:
        candlesticks = await hyperliquid_service.get_candlestick_data(
            coin.upper(), interval, limit
        )
        return APIResponse(
            success=True,
            message="Candlestick data retrieved successfully",
            data=[c.dict() for c in candlesticks]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/{coin}", response_model=APIResponse)
async def get_order_book(coin: str):
    """Get order book for a coin"""
    try:
        order_book = await hyperliquid_service.get_order_book(coin.upper())
        return APIResponse(
            success=True,
            message="Order book retrieved successfully",
            data=order_book.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trading endpoints
@app.post("/api/orders", response_model=APIResponse)
async def place_order(order_request: OrderRequest):
    """Place a trading order"""
    try:
        order = await hyperliquid_service.place_order(
            coin=order_request.coin.upper(),
            is_buy=order_request.is_buy,
            size=order_request.sz,
            price=order_request.limit_px,
            order_type=order_request.order_type,
            reduce_only=order_request.reduce_only
        )
        
        # Store order in database
        await db.orders.insert_one(order.dict())
        
        return APIResponse(
            success=True,
            message="Order placed successfully",
            data=order.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/orders/{coin}/{oid}", response_model=APIResponse)
async def cancel_order(coin: str, oid: int):
    """Cancel an order"""
    try:
        success = await hyperliquid_service.cancel_order(coin.upper(), oid)
        
        if success:
            # Update order status in database
            await db.orders.update_one(
                {"oid": oid},
                {"$set": {"status": OrderStatus.CANCELLED, "updated_at": datetime.utcnow()}}
            )
        
        return APIResponse(
            success=success,
            message="Order cancelled successfully" if success else "Failed to cancel order"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/open", response_model=APIResponse)
async def get_open_orders():
    """Get all open orders"""
    try:
        orders = await hyperliquid_service.get_open_orders()
        return APIResponse(
            success=True,
            message="Open orders retrieved successfully",
            data=[order.dict() for order in orders]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/history", response_model=APIResponse)
async def get_order_history(limit: int = 50):
    """Get order history"""
    try:
        orders = await hyperliquid_service.get_order_history(limit)
        return APIResponse(
            success=True,
            message="Order history retrieved successfully",
            data=[order.dict() for order in orders]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Strategy endpoints
@app.get("/api/strategies", response_model=APIResponse)
async def get_strategies():
    """Get all trading strategies"""
    try:
        strategies_cursor = db.strategies.find({})
        strategies = []
        async for strategy in strategies_cursor:
            strategy.pop("_id", None)
            strategies.append(strategy)
        
        return APIResponse(
            success=True,
            message="Strategies retrieved successfully",
            data=strategies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategies", response_model=APIResponse)
async def create_strategy(strategy: Strategy):
    """Create a new trading strategy"""
    try:
        await db.strategies.insert_one(strategy.dict())
        return APIResponse(
            success=True,
            message="Strategy created successfully",
            data=strategy.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/strategies/{strategy_id}", response_model=APIResponse)
async def update_strategy(strategy_id: str, strategy: Strategy):
    """Update a trading strategy"""
    try:
        result = await db.strategies.update_one(
            {"id": strategy_id},
            {"$set": {**strategy.dict(), "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return APIResponse(
            success=True,
            message="Strategy updated successfully",
            data=strategy.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/strategies/{strategy_id}", response_model=APIResponse)
async def delete_strategy(strategy_id: str):
    """Delete a trading strategy"""
    try:
        result = await db.strategies.delete_one({"id": strategy_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return APIResponse(
            success=True,
            message="Strategy deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Settings endpoints
@app.get("/api/settings", response_model=APIResponse)
async def get_settings():
    """Get user settings"""
    try:
        settings = await get_user_settings()
        return APIResponse(
            success=True,
            message="Settings retrieved successfully",
            data=settings.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/settings", response_model=APIResponse)
async def update_settings(settings: UserSettings):
    """Update user settings"""
    try:
        await db.user_settings.update_one(
            {},
            {"$set": {**settings.dict(), "updated_at": datetime.utcnow()}},
            upsert=True
        )
        
        # Update environment variables if API credentials changed
        if settings.api_credentials.wallet_address or settings.api_credentials.api_key or settings.api_credentials.api_secret:
            if settings.api_credentials.wallet_address:
                os.environ["HYPERLIQUID_WALLET_ADDRESS"] = settings.api_credentials.wallet_address.strip()
            if settings.api_credentials.api_key:
                os.environ["HYPERLIQUID_API_KEY"] = settings.api_credentials.api_key.strip()
            if settings.api_credentials.api_secret:
                os.environ["HYPERLIQUID_API_SECRET"] = settings.api_credentials.api_secret.strip()
            os.environ["HYPERLIQUID_ENV"] = settings.api_credentials.environment
            
            # Reinitialize service with new credentials from database
            print("Reinitializing Hyperliquid service with new credentials...")
            global hyperliquid_service
            from hyperliquid_service import HyperliquidService
            hyperliquid_service = HyperliquidService(
                wallet_address=settings.api_credentials.wallet_address,
                api_key=settings.api_credentials.api_key,
                api_secret=settings.api_credentials.api_secret,
                environment=settings.api_credentials.environment
            )
            print(f"Service reinitialized. Configured: {hyperliquid_service.is_configured}")
        
        return APIResponse(
            success=True,
            message="Settings updated successfully",
            data=settings.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings/api-status", response_model=APIResponse)
async def get_api_status():
    """Check if Hyperliquid API is configured and working"""
    try:
        # Get current settings from database to check actual configuration
        settings = await get_user_settings()
        
        # Check if API credentials are configured in the database
        is_configured = (
            settings.api_credentials.wallet_address and 
            settings.api_credentials.api_key and 
            settings.api_credentials.api_secret and
            settings.api_credentials.wallet_address.strip() != "" and
            settings.api_credentials.api_key.strip() != "" and
            settings.api_credentials.api_secret.strip() != ""
        )
        
        # Test API connection if configured
        test_result = None
        wallet_display = None
        
        if is_configured:
            wallet_display = f"{settings.api_credentials.wallet_address[:8]}...{settings.api_credentials.wallet_address[-8:]}"
            
            try:
                # Test basic API connection with public endpoint
                import requests
                test_response = requests.post(
                    "https://api.hyperliquid.xyz/info",
                    json={"type": "meta"},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if test_response.status_code == 200:
                    test_result = "✅ API connection successful - Ready for trading!"
                else:
                    test_result = f"❌ API connection failed: HTTP {test_response.status_code}"
                    
            except Exception as e:
                test_result = f"❌ Connection failed: {str(e)}"
        else:
            test_result = "⚠️ Please enter all three API credentials (wallet address, API key, and API secret key)"
        
        return APIResponse(
            success=True,
            message="API status retrieved successfully",
            data={
                "is_configured": is_configured,
                "environment": settings.api_credentials.environment,
                "test_result": test_result,
                "wallet_address": wallet_display,
                "credentials_status": {
                    "wallet_address": bool(settings.api_credentials.wallet_address and settings.api_credentials.wallet_address.strip()),
                    "api_key": bool(settings.api_credentials.api_key and settings.api_credentials.api_key.strip()),
                    "api_secret": bool(settings.api_credentials.api_secret and settings.api_credentials.api_secret.strip())
                }
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message="Failed to check API status",
            error=str(e),
            data={
                "is_configured": False,
                "environment": "unknown",
                "test_result": f"❌ Error checking status: {str(e)}"
            }
        )

# WebSocket endpoint for real-time data
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe_market":
                coin = message.get("coin", "BTC")
                # Start sending market data updates
                asyncio.create_task(send_market_updates(websocket, coin))
            elif message.get("type") == "subscribe_portfolio":
                # Start sending portfolio updates
                asyncio.create_task(send_portfolio_updates(websocket))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def send_market_updates(websocket: WebSocket, coin: str):
    """Send periodic market data updates"""
    while True:
        try:
            market_data = await hyperliquid_service.get_market_data(coin)
            await manager.send_personal_message({
                "type": "market_update",
                "coin": coin,
                "data": market_data.dict()
            }, websocket)
            await asyncio.sleep(5)  # Update every 5 seconds
        except:
            break

async def send_portfolio_updates(websocket: WebSocket):
    """Send periodic portfolio updates"""
    while True:
        try:
            portfolio = await hyperliquid_service.get_portfolio()
            await manager.send_personal_message({
                "type": "portfolio_update",
                "data": portfolio.dict()
            }, websocket)
            await asyncio.sleep(10)  # Update every 10 seconds
        except:
            break

@app.get("/api/coins", response_model=APIResponse)
async def get_available_coins():
    """Get list of available coins for trading from real Hyperliquid API"""
    try:
        import requests
        
        # Get real coin list from Hyperliquid meta endpoint
        meta_response = requests.post(
            "https://api.hyperliquid.xyz/info",
            json={"type": "meta"},
            headers={"Content-Type": "application/json"}
        )
        
        if meta_response.status_code == 200:
            meta_data = meta_response.json()
            
            coins = []
            for universe_item in meta_data.get("universe", []):
                coin_name = universe_item.get("name", "")
                if coin_name and not universe_item.get("isDelisted", False):
                    # Add display name based on common knowledge
                    display_names = {
                        "BTC": "Bitcoin",
                        "ETH": "Ethereum", 
                        "SOL": "Solana",
                        "AVAX": "Avalanche",
                        "MATIC": "Polygon",
                        "LINK": "Chainlink",
                        "UNI": "Uniswap",
                        "AAVE": "Aave",
                        "ATOM": "Cosmos",
                        "DOT": "Polkadot",
                        "ADA": "Cardano",
                        "NEAR": "Near Protocol",
                        "FIL": "Filecoin",
                        "DOGE": "Dogecoin",
                        "LTC": "Litecoin"
                    }
                    
                    coins.append({
                        "symbol": coin_name,
                        "name": display_names.get(coin_name, coin_name),
                        "maxLeverage": universe_item.get("maxLeverage", 1)
                    })
            
            # Sort by symbol for better UX
            coins.sort(key=lambda x: x["symbol"])
            
            return APIResponse(
                success=True,
                message="Available coins retrieved successfully",
                data=coins
            )
        
        raise Exception("Could not fetch real coin list")
        
    except Exception as e:
        print(f"Error fetching real coin list: {e}")
        # Fallback to a basic list of major coins
        fallback_coins = [
            {"symbol": "BTC", "name": "Bitcoin", "maxLeverage": 40},
            {"symbol": "ETH", "name": "Ethereum", "maxLeverage": 25},
            {"symbol": "SOL", "name": "Solana", "maxLeverage": 20},
            {"symbol": "AVAX", "name": "Avalanche", "maxLeverage": 10},
            {"symbol": "LINK", "name": "Chainlink", "maxLeverage": 10},
            {"symbol": "UNI", "name": "Uniswap", "maxLeverage": 10},
            {"symbol": "AAVE", "name": "Aave", "maxLeverage": 10},
            {"symbol": "ATOM", "name": "Cosmos", "maxLeverage": 5},
        ]
        
        return APIResponse(
            success=True,
            message="Available coins retrieved successfully (fallback)",
            data=fallback_coins
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
