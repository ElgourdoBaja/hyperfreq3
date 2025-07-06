import requests
import sys
import json
from datetime import datetime

class HyperliquidRealDataTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, params=None, validation_func=None):
        """Run a single API test with optional validation function"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            
            status_success = response.status_code == expected_status
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"error": "Could not parse JSON response"}
            
            # Run validation function if provided
            validation_success = True
            validation_message = ""
            if status_success and validation_func:
                validation_success, validation_message = validation_func(response_data)
            
            success = status_success and validation_success
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if validation_message:
                    print(f"   {validation_message}")
            else:
                if not status_success:
                    print(f"❌ Failed - Expected status {expected_status}, got {response.status_code}")
                if not validation_success:
                    print(f"❌ Failed - {validation_message}")
            
            # Store test result
            self.test_results.append({
                "name": name,
                "success": success,
                "status_code": response.status_code,
                "validation_message": validation_message,
                "response_data": response_data
            })
            
            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "error": str(e)
            })
            return False, {}

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        # Print failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['name']}")
                if "error" in test:
                    print(f"    Error: {test['error']}")
                elif "validation_message" in test and test["validation_message"]:
                    print(f"    Reason: {test['validation_message']}")
        print("="*50)

def validate_real_market_data(response_data):
    """Validate that market data appears to be real"""
    if not response_data.get("success"):
        return False, "API response indicates failure"
    
    data = response_data.get("data", {})
    
    # Check if price exists and is reasonable
    if "price" not in data:
        return False, "No price data found"
    
    price = data.get("price")
    if not isinstance(price, (int, float)) or price <= 0:
        return False, f"Invalid price value: {price}"
    
    # Check if bid/ask spread is reasonable
    bid = data.get("bid")
    ask = data.get("ask")
    if not all([isinstance(x, (int, float)) for x in [bid, ask]]):
        return False, "Invalid bid/ask values"
    
    if bid >= ask:
        return False, f"Invalid bid/ask relationship: bid={bid}, ask={ask}"
    
    # For BTC, check if price is in a reasonable range for real data
    coin = data.get("coin")
    if coin == "BTC" and (price < 10000 or price > 500000):
        return False, f"BTC price {price} seems unrealistic"
    elif coin == "ETH" and (price < 500 or price > 50000):
        return False, f"ETH price {price} seems unrealistic"
    
    return True, f"Real market data verified: {coin} price=${price:.2f}, bid=${bid:.2f}, ask=${ask:.2f}"

def validate_order_book(response_data):
    """Validate that order book data appears to be real"""
    if not response_data.get("success"):
        return False, "API response indicates failure"
    
    data = response_data.get("data", {})
    
    # Check if bids and asks exist
    if "bids" not in data or "asks" not in data:
        return False, "No bids or asks data found"
    
    bids = data.get("bids", [])
    asks = data.get("asks", [])
    
    # Check if there are enough orders
    if len(bids) < 3 or len(asks) < 3:
        return False, f"Not enough orders in book: {len(bids)} bids, {len(asks)} asks"
    
    # Check if bids are in descending order
    for i in range(1, len(bids)):
        if bids[i-1]["price"] < bids[i]["price"]:
            return False, "Bids are not in descending order"
    
    # Check if asks are in ascending order
    for i in range(1, len(asks)):
        if asks[i-1]["price"] > asks[i]["price"]:
            return False, "Asks are not in ascending order"
    
    # Check if there's a reasonable spread
    if bids[0]["price"] >= asks[0]["price"]:
        return False, f"Invalid spread: highest bid ${bids[0]['price']} >= lowest ask ${asks[0]['price']}"
    
    return True, f"Real order book verified: {len(bids)} bids, {len(asks)} asks, spread=${asks[0]['price'] - bids[0]['price']:.2f}"

def validate_candlestick_data(response_data):
    """Validate that candlestick data appears to be real"""
    if not response_data.get("success"):
        return False, "API response indicates failure"
    
    data = response_data.get("data", [])
    
    # Check if there are enough candles
    if len(data) < 10:
        return False, f"Not enough candles: {len(data)}"
    
    # Check if candles have required fields
    required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
    for candle in data[:5]:  # Check first 5 candles
        for field in required_fields:
            if field not in candle:
                return False, f"Candle missing required field: {field}"
    
    # Check if high is always >= low
    for candle in data:
        if candle["high"] < candle["low"]:
            return False, f"Invalid candle: high ${candle['high']} < low ${candle['low']}"
    
    # Check if timestamps are sequential
    for i in range(1, len(data)):
        t1 = datetime.fromisoformat(data[i-1]["timestamp"].replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(data[i]["timestamp"].replace("Z", "+00:00"))
        if t1 <= t2:  # Changed from t1 >= t2 to t1 <= t2 since older timestamps come first
            continue
        else:
            return False, "Candle timestamps are not sequential"
    
    return True, f"Real candlestick data verified: {len(data)} candles"

def validate_coins_list(response_data):
    """Validate that the coins list appears to be real"""
    if not response_data.get("success"):
        return False, "API response indicates failure"
    
    data = response_data.get("data", [])
    
    # Check if there are enough coins
    if len(data) < 50:  # Hyperliquid has 143+ coins, but we'll be conservative
        return False, f"Not enough coins: {len(data)}"
    
    # Check if major coins are present
    major_coins = ["BTC", "ETH", "SOL", "AVAX"]
    found_coins = [coin["symbol"] for coin in data]
    
    missing_coins = [coin for coin in major_coins if coin not in found_coins]
    if missing_coins:
        return False, f"Missing major coins: {', '.join(missing_coins)}"
    
    # Check if coins have required fields
    required_fields = ["symbol", "name", "maxLeverage"]
    for coin in data[:5]:  # Check first 5 coins
        for field in required_fields:
            if field not in coin:
                return False, f"Coin missing required field: {field}"
    
    return True, f"Real coins list verified: {len(data)} coins available"

def main():
    # Get backend URL from frontend .env file
    backend_url = "https://1341ecb2-a30c-43a3-ad39-cb81c20c3586.preview.emergentagent.com"
    
    print(f"Testing Hypertrader 1.5 Real Data API at: {backend_url}")
    tester = HyperliquidRealDataTester(backend_url)
    
    # Test API health
    tester.run_test(
        "API Health Check",
        "GET",
        "api/health",
        200,
        validation_func=lambda resp: (resp.get("status") == "healthy", "API is healthy")
    )
    
    # Test real market data for multiple coins
    for coin in ["BTC", "ETH", "SOL", "AVAX"]:
        tester.run_test(
            f"Real Market Data - {coin}",
            "GET",
            f"api/market/{coin}",
            200,
            validation_func=validate_real_market_data
        )
    
    # Test real order book data
    for coin in ["BTC", "ETH"]:
        tester.run_test(
            f"Real Order Book - {coin}",
            "GET",
            f"api/orderbook/{coin}",
            200,
            validation_func=validate_order_book
        )
    
    # Test real candlestick data
    for coin in ["BTC", "ETH"]:
        tester.run_test(
            f"Real Candlestick Data - {coin}",
            "GET",
            f"api/candlesticks/{coin}?interval=1h&limit=100",
            200,
            validation_func=validate_candlestick_data
        )
    
    # Test real coins list
    tester.run_test(
        "Real Coins List",
        "GET",
        "api/coins",
        200,
        validation_func=validate_coins_list
    )
    
    # Print test summary
    tester.print_summary()
    
    # Return success if all tests passed
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())