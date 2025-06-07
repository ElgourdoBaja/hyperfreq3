
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

    def run_test(self, name, method, endpoint, expected_status=200, data=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                result = {
                    "name": name,
                    "status": "PASS",
                    "response_code": response.status_code,
                    "data": response.json() if response.text else None
                }
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                result = {
                    "name": name,
                    "status": "FAIL",
                    "response_code": response.status_code,
                    "error": response.text
                }
            
            self.test_results.append(result)
            return success, response.json() if success and response.text else None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False, None

    def test_health(self):
        """Test the health endpoint"""
        return self.run_test("Health Check", "GET", "/api/health")

    def test_root(self):
        """Test the root endpoint"""
        return self.run_test("Root Endpoint", "GET", "/api/")

    def test_portfolio(self):
        """Test the portfolio endpoint"""
        return self.run_test("Portfolio Data", "GET", "/api/portfolio")

    def test_account(self):
        """Test the account endpoint"""
        return self.run_test("Account Info", "GET", "/api/account")

    def test_market_data(self, coin="BTC"):
        """Test market data for a specific coin"""
        return self.run_test(f"Market Data ({coin})", "GET", f"/api/market/{coin}")

    def test_candlesticks(self, coin="BTC"):
        """Test candlestick data for a specific coin"""
        return self.run_test(f"Candlestick Data ({coin})", "GET", f"/api/candlesticks/{coin}")

    def test_orderbook(self, coin="BTC"):
        """Test order book for a specific coin"""
        return self.run_test(f"Order Book ({coin})", "GET", f"/api/orderbook/{coin}")

    def test_open_orders(self):
        """Test open orders endpoint"""
        return self.run_test("Open Orders", "GET", "/api/orders/open")

    def test_order_history(self):
        """Test order history endpoint"""
        return self.run_test("Order History", "GET", "/api/orders/history")

    def test_strategies(self):
        """Test strategies endpoint"""
        return self.run_test("Strategies", "GET", "/api/strategies")

    def test_settings(self):
        """Test settings endpoint"""
        return self.run_test("Settings", "GET", "/api/settings")

    def test_api_status(self):
        """Test API status endpoint"""
        return self.run_test("API Status", "GET", "/api/settings/api-status")

    def test_coins(self):
        """Test available coins endpoint"""
        return self.run_test("Available Coins", "GET", "/api/coins")

    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*50)
        print(f"📊 TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        # Group by status
        passed = [t for t in self.test_results if t["status"] == "PASS"]
        failed = [t for t in self.test_results if t["status"] == "FAIL"]
        errors = [t for t in self.test_results if t["status"] == "ERROR"]
        
        if passed:
            print(f"\n✅ PASSED TESTS ({len(passed)}):")
            for test in passed:
                print(f"  - {test['name']}")
        
        if failed:
            print(f"\n❌ FAILED TESTS ({len(failed)}):")
            for test in failed:
                print(f"  - {test['name']} (Status: {test['response_code']})")
        
        if errors:
            print(f"\n⚠️ ERRORS ({len(errors)}):")
            for test in errors:
                print(f"  - {test['name']}: {test['error']}")
        
        print("\n" + "="*50)
        
        # Check for specific data in responses
        self.analyze_responses()
        
    def analyze_responses(self):
        """Analyze response data for specific information"""
        print("\n🔍 DETAILED ANALYSIS:")
        
        # Check account data
        account_test = next((t for t in self.test_results if t["name"] == "Account Info" and t["status"] == "PASS"), None)
        if account_test and account_test.get("data"):
            account_data = account_test["data"].get("data", {})
            wallet_address = account_data.get("address", "Not found")
            print(f"👛 Wallet Address: {wallet_address}")
        
        # Check portfolio data
        portfolio_test = next((t for t in self.test_results if t["name"] == "Portfolio Data" and t["status"] == "PASS"), None)
        if portfolio_test and portfolio_test.get("data"):
            portfolio_data = portfolio_test["data"].get("data", {})
            account_value = portfolio_data.get("account_value", "Not found")
            available_balance = portfolio_data.get("available_balance", "Not found")
            positions = portfolio_data.get("positions", [])
            
            print(f"💰 Account Value: ${account_value}")
            print(f"💵 Available Balance: ${available_balance}")
            print(f"📊 Number of Positions: {len(positions)}")
            
            if positions:
                print("\nPositions:")
                for pos in positions:
                    print(f"  - {pos.get('coin')}: {pos.get('size')} @ ${pos.get('entry_price')}")
        
        # Check API status
        api_status_test = next((t for t in self.test_results if t["name"] == "API Status" and t["status"] == "PASS"), None)
        if api_status_test and api_status_test.get("data"):
            status_data = api_status_test["data"].get("data", {})
            is_configured = status_data.get("is_configured", False)
            test_result = status_data.get("test_result", "Unknown")
            
            print(f"\n🔌 API Configuration: {'Configured' if is_configured else 'Not Configured'}")
            print(f"🧪 API Test Result: {test_result}")
        
        # Check market data
        market_tests = [t for t in self.test_results if t["name"].startswith("Market Data") and t["status"] == "PASS"]
        if market_tests:
            print("\n📈 Market Data:")
            for test in market_tests:
                if test.get("data") and test["data"].get("data"):
                    coin = test["data"]["data"].get("coin", "Unknown")
                    price = test["data"]["data"].get("price", "Unknown")
                    print(f"  - {coin}: ${price}")

def main():
    # Setup
    tester = HypertraderAPITester()
    
    # Basic API tests
    tester.test_health()
    tester.test_root()
    
    # Core data tests
    tester.test_portfolio()
    tester.test_account()
    
    # Market data tests
    for coin in ["BTC", "ETH", "SOL", "AVAX"]:
        tester.test_market_data(coin)
        tester.test_candlesticks(coin)
        tester.test_orderbook(coin)
    
    # Trading data tests
    tester.test_open_orders()
    tester.test_order_history()
    
    # Strategy and settings tests
    tester.test_strategies()
    tester.test_settings()
    tester.test_api_status()
    tester.test_coins()
    
    # Print results
    tester.print_summary()
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
