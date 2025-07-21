import requests
import json
import sys
import time
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                result = {
                    "name": name,
                    "status": "PASSED",
                    "response": response.json() if response.text else {}
                }
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                result = {
                    "name": name,
                    "status": "FAILED",
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "response": response.json() if response.text else {}
                }
            
            self.test_results.append(result)
            return success, response.json() if response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "name": name,
                "status": "ERROR",
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    # Health Check
    def test_health_check(self):
        """Test the health check endpoint"""
        print("\n📋 Testing /api/health endpoint...")
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            if response.get("status") == "healthy":
                print("✅ API is healthy")
            else:
                print("❌ API is not reporting as healthy")
                success = False
        
        return success, response

    # Portfolio Endpoints
    def test_get_portfolio(self):
        """Test getting portfolio data"""
        print("\n📋 Testing GET /api/portfolio endpoint...")
        success, response = self.run_test(
            "Get Portfolio",
            "GET",
            "api/portfolio",
            200
        )
        
        if success:
            data = response.get("data", {})
            if "account_value" in data and "positions" in data:
                print("✅ Portfolio data structure is valid")
            else:
                print("❌ Portfolio data structure is invalid")
                success = False
        
        return success, response

    def test_get_account_info(self):
        """Test getting account information"""
        print("\n📋 Testing GET /api/account endpoint...")
        success, response = self.run_test(
            "Get Account Info",
            "GET",
            "api/account",
            200
        )
        
        if success:
            data = response.get("data", {})
            if "account_value" in data and "address" in data:
                print("✅ Account data structure is valid")
            else:
                print("❌ Account data structure is invalid")
                success = False
        
        return success, response

    # Market Data Endpoints
    def test_get_market_data(self, coin="BTC"):
        """Test getting market data for a coin"""
        print(f"\n📋 Testing GET /api/market/{coin} endpoint...")
        success, response = self.run_test(
            f"Get Market Data for {coin}",
            "GET",
            f"api/market/{coin}",
            200
        )
        
        if success:
            data = response.get("data", {})
            if "price" in data and "coin" in data:
                print(f"✅ Market data structure for {coin} is valid")
            else:
                print(f"❌ Market data structure for {coin} is invalid")
                success = False
        
        return success, response

    def test_get_candlestick_data(self, coin="BTC", interval="1h", limit=10):
        """Test getting candlestick data for a coin"""
        print(f"\n📋 Testing GET /api/candlesticks/{coin} endpoint...")
        success, response = self.run_test(
            f"Get Candlestick Data for {coin}",
            "GET",
            f"api/candlesticks/{coin}?interval={interval}&limit={limit}",
            200
        )
        
        if success:
            data = response.get("data", [])
            if isinstance(data, list) and len(data) > 0:
                first_candle = data[0]
                if "open" in first_candle and "close" in first_candle:
                    print(f"✅ Candlestick data structure for {coin} is valid")
                else:
                    print(f"❌ Candlestick data structure for {coin} is invalid")
                    success = False
            else:
                print(f"❌ No candlestick data returned for {coin}")
                success = False
        
        return success, response

    def test_get_order_book(self, coin="BTC"):
        """Test getting order book for a coin"""
        print(f"\n📋 Testing GET /api/orderbook/{coin} endpoint...")
        success, response = self.run_test(
            f"Get Order Book for {coin}",
            "GET",
            f"api/orderbook/{coin}",
            200
        )
        
        if success:
            data = response.get("data", {})
            if "bids" in data and "asks" in data:
                print(f"✅ Order book data structure for {coin} is valid")
            else:
                print(f"❌ Order book data structure for {coin} is invalid")
                success = False
        
        return success, response

    # Trading Endpoints
    def test_place_order(self, coin="BTC"):
        """Test placing an order"""
        print("\n📋 Testing POST /api/orders endpoint...")
        
        # Create a small limit order
        order_data = {
            "coin": coin,
            "is_buy": True,
            "sz": 0.01,  # Small size for testing
            "limit_px": 40000,  # Limit price
            "order_type": "limit",
            "time_in_force": "Gtc",
            "reduce_only": False
        }
        
        success, response = self.run_test(
            "Place Limit Order",
            "POST",
            "api/orders",
            200,
            data=order_data
        )
        
        if success:
            data = response.get("data", {})
            if "id" in data and "status" in data:
                print("✅ Order placement successful")
            else:
                print("❌ Order placement response structure is invalid")
                success = False
        
        return success, response

    def test_get_open_orders(self):
        """Test getting open orders"""
        print("\n📋 Testing GET /api/orders/open endpoint...")
        success, response = self.run_test(
            "Get Open Orders",
            "GET",
            "api/orders/open",
            200
        )
        
        if success:
            data = response.get("data", [])
            if isinstance(data, list):
                print(f"✅ Open orders data structure is valid, found {len(data)} orders")
            else:
                print("❌ Open orders data structure is invalid")
                success = False
        
        return success, response

    def test_get_order_history(self):
        """Test getting order history"""
        print("\n📋 Testing GET /api/orders/history endpoint...")
        success, response = self.run_test(
            "Get Order History",
            "GET",
            "api/orders/history",
            200
        )
        
        if success:
            data = response.get("data", [])
            if isinstance(data, list):
                print(f"✅ Order history data structure is valid, found {len(data)} orders")
            else:
                print("❌ Order history data structure is invalid")
                success = False
        
        return success, response

    # Strategy Endpoints
    def test_strategy_crud(self):
        """Test CRUD operations for strategies"""
        print("\n📋 Testing Strategy CRUD operations...")
        
        # 1. Get initial strategies
        success, initial_response = self.run_test(
            "Get Initial Strategies",
            "GET",
            "api/strategies",
            200
        )
        
        if not success:
            return False, initial_response
        
        initial_count = len(initial_response.get("data", []))
        print(f"Initial strategy count: {initial_count}")
        
        # 2. Create a new strategy
        strategy_data = {
            "id": f"test-strategy-{int(time.time())}",
            "name": "Test Strategy",
            "description": "A test strategy created by the API tester",
            "coin": "BTC",
            "status": "active",
            "config": {
                "entry_conditions": {"price_above": 40000},
                "exit_conditions": {"price_below": 38000},
                "risk_management": {"stop_loss": 0.05},
                "position_sizing": {"percentage": 0.1}
            }
        }
        
        success, create_response = self.run_test(
            "Create Strategy",
            "POST",
            "api/strategies",
            200,
            data=strategy_data
        )
        
        if not success:
            return False, create_response
        
        strategy_id = strategy_data["id"]
        
        # 3. Verify strategy was created
        success, get_response = self.run_test(
            "Get Strategies After Creation",
            "GET",
            "api/strategies",
            200
        )
        
        if success:
            new_count = len(get_response.get("data", []))
            if new_count > initial_count:
                print(f"✅ Strategy count increased from {initial_count} to {new_count}")
            else:
                print("❌ Strategy count did not increase after creation")
                success = False
        
        if not success:
            return False, get_response
        
        # 4. Update the strategy
        updated_strategy = strategy_data.copy()
        updated_strategy["name"] = "Updated Test Strategy"
        updated_strategy["description"] = "This strategy has been updated"
        
        success, update_response = self.run_test(
            "Update Strategy",
            "PUT",
            f"api/strategies/{strategy_id}",
            200,
            data=updated_strategy
        )
        
        if not success:
            return False, update_response
        
        # 5. Delete the strategy
        success, delete_response = self.run_test(
            "Delete Strategy",
            "DELETE",
            f"api/strategies/{strategy_id}",
            200
        )
        
        if success:
            print("✅ Strategy CRUD operations completed successfully")
        
        return success, delete_response

    # Settings Endpoints
    def test_get_settings(self):
        """Test getting user settings"""
        print("\n📋 Testing GET /api/settings endpoint...")
        success, response = self.run_test(
            "Get Settings",
            "GET",
            "api/settings",
            200
        )
        
        if success:
            data = response.get("data", {})
            if "api_credentials" in data:
                print("✅ Settings data structure is valid")
            else:
                print("❌ Settings data structure is invalid")
                success = False
        
        return success, response

    def test_update_settings(self):
        """Test updating user settings"""
        print("\n📋 Testing PUT /api/settings endpoint...")
        
        # First get current settings
        _, current_settings = self.run_test(
            "Get Current Settings",
            "GET",
            "api/settings",
            200
        )
        
        if not current_settings:
            print("❌ Could not get current settings to update")
            return False, {}
        
        # Prepare test data with API credentials
        test_data = current_settings.get("data", {})
        test_data["api_credentials"] = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "api_key": "test_api_key_123",
            "api_secret": "test_api_secret_456",
            "environment": "testnet",
            "is_configured": True
        }
        
        # Update settings
        success, response = self.run_test(
            "Update Settings",
            "PUT",
            "api/settings",
            200,
            data=test_data
        )
        
        if success:
            print("✅ Successfully updated settings")
        
        return success, response

    def test_api_status(self):
        """Test the API status endpoint"""
        print("\n📋 Testing GET /api/settings/api-status endpoint...")
        success, response = self.run_test(
            "Get API Status",
            "GET",
            "api/settings/api-status",
            200
        )
        
        if success:
            data = response.get("data", {})
            if "is_configured" in data and "environment" in data:
                print("✅ API status data structure is valid")
            else:
                print("❌ API status data structure is invalid")
                success = False
        
        return success, response

    # Available Coins Endpoint
    def test_get_available_coins(self):
        """Test getting available coins"""
        print("\n📋 Testing GET /api/coins endpoint...")
        success, response = self.run_test(
            "Get Available Coins",
            "GET",
            "api/coins",
            200
        )
        
        if success:
            data = response.get("data", [])
            if isinstance(data, list) and len(data) > 0:
                first_coin = data[0]
                if "symbol" in first_coin and "name" in first_coin:
                    print(f"✅ Available coins data structure is valid, found {len(data)} coins")
                else:
                    print("❌ Available coins data structure is invalid")
                    success = False
            else:
                print("❌ No coins returned")
                success = False
        
        return success, response

    def run_all_tests(self):
        """Run all tests and print a summary"""
        print("\n🚀 Starting Hypertrader 1.5 API Tests...")
        
        # Health check
        self.test_health_check()
        
        # Portfolio endpoints
        self.test_get_portfolio()
        self.test_get_account_info()
        
        # Market data endpoints
        self.test_get_market_data("BTC")
        self.test_get_candlestick_data("BTC")
        self.test_get_order_book("BTC")
        
        # Trading endpoints
        self.test_place_order()
        self.test_get_open_orders()
        self.test_get_order_history()
        
        # Strategy endpoints
        self.test_strategy_crud()
        
        # Settings endpoints
        self.test_get_settings()
        self.test_update_settings()
        self.test_api_status()
        
        # Available coins endpoint
        self.test_get_available_coins()
        
        # Print summary
        print("\n📊 Test Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run) * 100:.2f}%")
        
        # Print failed tests
        failed_tests = [test for test in self.test_results if test["status"] != "PASSED"]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"- {test['name']}: {test.get('error', 'Status code mismatch')}")
        
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://54bf5074-fbbb-49dd-a379-2b55c68d8cb8.preview.emergentagent.com"
    
    # Run the tests
    tester = HypertraderAPITester(backend_url)
    success = tester.run_all_tests()
    
    # Return exit code based on test results
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())