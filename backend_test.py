
import requests
import sys
import time
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                self.test_results.append({
                    "name": name,
                    "success": True,
                    "status_code": response.status_code
                })
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                self.test_results.append({
                    "name": name,
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"Expected {expected_status}, got {response.status_code}"
                })

            try:
                return success, response.json()
            except:
                return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "error": str(e)
            })
            return False, {}

    def test_health(self):
        """Test API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api/health",
            200
        )

    def test_account_info(self):
        """Test account info endpoint"""
        return self.run_test(
            "Account Info",
            "GET",
            "api/account",
            200
        )

    def test_portfolio(self):
        """Test portfolio endpoint"""
        return self.run_test(
            "Portfolio",
            "GET",
            "api/portfolio",
            200
        )

    def test_settings(self):
        """Test settings endpoint"""
        return self.run_test(
            "Settings",
            "GET",
            "api/settings",
            200
        )

    def test_api_status(self):
        """Test API status endpoint"""
        return self.run_test(
            "API Status",
            "GET",
            "api/settings/api-status",
            200
        )

    def test_coins(self):
        """Test available coins endpoint"""
        return self.run_test(
            "Available Coins",
            "GET",
            "api/coins",
            200
        )

    def test_market_data(self, coin="BTC"):
        """Test market data endpoint"""
        return self.run_test(
            f"Market Data for {coin}",
            "GET",
            f"api/market/{coin}",
            200
        )

    def test_candlestick_data(self, coin="BTC"):
        """Test candlestick data endpoint"""
        return self.run_test(
            f"Candlestick Data for {coin}",
            "GET",
            f"api/candlesticks/{coin}?interval=1h&limit=100",
            200
        )

    def test_order_book(self, coin="BTC"):
        """Test order book endpoint"""
        return self.run_test(
            f"Order Book for {coin}",
            "GET",
            f"api/orderbook/{coin}",
            200
        )

    def test_open_orders(self):
        """Test open orders endpoint"""
        return self.run_test(
            "Open Orders",
            "GET",
            "api/orders/open",
            200
        )

    def test_order_history(self):
        """Test order history endpoint"""
        return self.run_test(
            "Order History",
            "GET",
            "api/orders/history",
            200
        )

    def test_strategies(self):
        """Test strategies endpoint"""
        return self.run_test(
            "Strategies",
            "GET",
            "api/strategies",
            200
        )

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print(f"📊 API TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        if self.tests_passed < self.tests_run:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result.get("success"):
                    print(f"❌ {result['name']}: {result.get('error', 'Unknown error')}")
        
        print("\n")
        return self.tests_passed == self.tests_run

def main():
    # Get backend URL from frontend .env file
    backend_url = "https://675a754d-13da-4f9c-b1c7-a10e6ab42a32.preview.emergentagent.com"
    print(f"Testing Hypertrader 1.5 API at: {backend_url}")
    
    # Initialize tester
    tester = HypertraderAPITester(backend_url)
    
    # Run basic API tests
    tester.test_health()
    
    # Test account and portfolio endpoints
    account_success, account_data = tester.test_account_info()
    portfolio_success, portfolio_data = tester.test_portfolio()
    
    # Verify account balance is $135.49 as expected
    if account_success and account_data.get("success"):
        account_value = account_data.get("data", {}).get("account_value", 0)
        print(f"\n🔍 Checking account balance: ${account_value}")
        if abs(account_value - 135.49) < 0.01:
            print(f"✅ Account balance verified: ${account_value} matches expected $135.49")
        else:
            print(f"❌ Account balance mismatch: ${account_value} does not match expected $135.49")
    
    # Test settings endpoints
    tester.test_settings()
    tester.test_api_status()
    
    # Test market data endpoints
    tester.test_coins()
    tester.test_market_data()
    tester.test_candlestick_data()
    tester.test_order_book()
    
    # Test order endpoints
    tester.test_open_orders()
    tester.test_order_history()
    
    # Test strategy endpoints
    tester.test_strategies()
    
    # Print summary
    success = tester.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
