
import requests
import sys
import time
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url="https://675a754d-13da-4f9c-b1c7-a10e6ab42a32.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, check_data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            
            # Additional data validation if provided
            data_valid = True
            data_message = ""
            if success and check_data and response.status_code == 200:
                try:
                    resp_data = response.json()
                    data_valid, data_message = check_data(resp_data)
                    success = success and data_valid
                except Exception as e:
                    data_valid = False
                    data_message = f"Error validating response data: {str(e)}"
                    success = False
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if data_message:
                    print(f"   {data_message}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if data_message:
                    print(f"   {data_message}")
            
            # Store test result
            self.test_results.append({
                "name": name,
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "message": data_message
            })
            
            return success, response.json() if success and response.status_code != 204 else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out")
            self.test_results.append({
                "name": name,
                "success": False,
                "status_code": None,
                "expected_status": expected_status,
                "message": "Request timed out"
            })
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "status_code": None,
                "expected_status": expected_status,
                "message": str(e)
            })
            return False, {}

    def test_health(self):
        """Test health endpoint"""
        def check_health_data(data):
            if "status" in data and data["status"] == "healthy":
                return True, "Health status is healthy"
            return False, "Health status is not healthy"
        
        return self.run_test(
            "Health Check",
            "GET",
            "health",
            200,
            check_data=check_health_data
        )

    def test_get_coins(self):
        """Test getting available coins"""
        def check_coins_data(data):
            if not data.get("success", False):
                return False, "API response indicates failure"
            
            coins = data.get("data", [])
            if not coins or len(coins) < 170:
                return False, f"Expected at least 170 coins, got {len(coins)}"
            
            # Check if coins have required fields
            for coin in coins[:5]:  # Check first 5 coins
                if not all(key in coin for key in ["symbol", "name", "maxLeverage"]):
                    return False, f"Coin missing required fields: {coin}"
            
            return True, f"Found {len(coins)} coins with required data"
        
        return self.run_test(
            "Get Available Coins",
            "GET",
            "coins",
            200,
            check_data=check_coins_data
        )

    def test_get_market_data(self, coin="BTC"):
        """Test getting market data for a coin"""
        def check_market_data(data):
            if not data.get("success", False):
                return False, "API response indicates failure"
            
            market_data = data.get("data", {})
            required_fields = ["price", "bid", "ask", "change_24h", "volume_24h"]
            
            for field in required_fields:
                if field not in market_data:
                    return False, f"Market data missing required field: {field}"
            
            return True, f"Market data for {coin} contains all required fields"
        
        return self.run_test(
            f"Get Market Data for {coin}",
            "GET",
            f"market/{coin}",
            200,
            check_data=check_market_data
        )

    def test_get_orderbook(self, coin="BTC"):
        """Test getting orderbook for a coin"""
        def check_orderbook_data(data):
            if not data.get("success", False):
                return False, "API response indicates failure"
            
            orderbook = data.get("data", {})
            if "bids" not in orderbook or "asks" not in orderbook:
                return False, "Orderbook missing bids or asks"
            
            if not orderbook["bids"] or not orderbook["asks"]:
                return False, "Orderbook has empty bids or asks"
            
            return True, f"Orderbook for {coin} contains bids and asks"
        
        return self.run_test(
            f"Get Orderbook for {coin}",
            "GET",
            f"orderbook/{coin}",
            200,
            check_data=check_orderbook_data
        )

    def test_place_order(self, coin="BTC"):
        """Test placing an order (mock test)"""
        order_data = {
            "coin": coin,
            "is_buy": True,
            "sz": 0.001,
            "limit_px": 50000,
            "order_type": "limit",
            "reduce_only": False,
            "leverage": 1
        }
        
        # Note: We're not expecting this to succeed since we don't have real credentials
        # This is just to test the API endpoint structure
        return self.run_test(
            "Place Order (Mock)",
            "POST",
            "orders",
            500,  # Expecting error since we don't have real credentials
            data=order_data
        )

    def test_get_candlesticks(self, coin="BTC"):
        """Test getting candlestick data"""
        def check_candlestick_data(data):
            if not data.get("success", False):
                return False, "API response indicates failure"
            
            candlesticks = data.get("data", [])
            if not candlesticks:
                return False, "No candlestick data returned"
            
            # Check if candlesticks have required fields
            for candle in candlesticks[:3]:  # Check first 3 candles
                required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
                for field in required_fields:
                    if field not in candle:
                        return False, f"Candlestick missing required field: {field}"
            
            return True, f"Found {len(candlesticks)} candlesticks with required data"
        
        return self.run_test(
            f"Get Candlestick Data for {coin}",
            "GET",
            f"candlesticks/{coin}",
            200,
            check_data=check_candlestick_data
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Hypertrader API Tests...")
        
        # Basic API tests
        self.test_health()
        
        # Market data tests
        self.test_get_coins()
        
        # Test with multiple coins
        test_coins = ["BTC", "ETH", "SOL"]
        for coin in test_coins:
            self.test_get_market_data(coin)
            self.test_get_orderbook(coin)
            self.test_get_candlesticks(coin)
        
        # Trading tests (mock)
        self.test_place_order()
        
        # Print summary
        print("\n📊 Test Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.2f}%")
        
        # Print detailed results
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} - {result['name']}")
            if not result["success"] and result["message"]:
                print(f"       {result['message']}")
        
        return self.tests_passed == self.tests_run

def main():
    # Get backend URL from environment or use default
    tester = HypertraderAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
