
import requests
import sys
import json
from datetime import datetime
import time

class HypertraderAPITester:
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            status_success = response.status_code == expected_status
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.status_code != 204 else {}
            except:
                response_data = {"error": "Could not parse JSON response"}
            
            # Run validation function if provided
            validation_success = True
            validation_message = ""
            if status_success and validation_func and response.status_code != 204:
                validation_success, validation_message = validation_func(response_data)
            
            success = status_success and validation_success
            
            result = {
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if validation_message:
                    print(f"   {validation_message}")
                if response.status_code != 204:
                    result["response"] = response_data
            else:
                if not status_success:
                    print(f"❌ Failed - Expected status {expected_status}, got {response.status_code}")
                if not validation_success:
                    print(f"❌ Failed - {validation_message}")
                try:
                    result["error"] = response_data
                except:
                    result["error"] = response.text

            self.test_results.append(result)
            return success, response_data if success else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e)
            })
            return False, {}

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print(f"📊 TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        # Print failed tests
        if self.tests_passed < self.tests_run:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"- {result['name']} ({result['method']} {result['endpoint']})")
                    if "error" in result:
                        print(f"  Error: {result['error']}")
        print("="*50)

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://675a754d-13da-4f9c-b1c7-a10e6ab42a32.preview.emergentagent.com"
    
    print(f"Testing Hypertrader 1.5 API at: {backend_url}")
    tester = HypertraderAPITester(backend_url)
    
    # 1. Test Health Endpoint
    tester.run_test("Health Check", "GET", "api/health")
    
    # 2. Test Root Endpoint
    tester.run_test("Root Endpoint", "GET", "api/")
    
    # 3. Test Portfolio Endpoint
    tester.run_test("Get Portfolio", "GET", "api/portfolio")
    
    # 4. Test Account Info Endpoint
    tester.run_test("Get Account Info", "GET", "api/account")
    
    # 5. Test Market Data Endpoints
    tester.run_test("Get Market Data - BTC", "GET", "api/market/BTC")
    tester.run_test("Get Market Data - ETH", "GET", "api/market/ETH")
    
    # 6. Test Candlestick Data
    tester.run_test("Get Candlestick Data - BTC", "GET", "api/candlesticks/BTC", params={"interval": "1h", "limit": 50})
    
    # 7. Test Order Book
    tester.run_test("Get Order Book - BTC", "GET", "api/orderbook/BTC")
    
    # 8. Test Open Orders
    tester.run_test("Get Open Orders", "GET", "api/orders/open")
    
    # 9. Test Order History
    tester.run_test("Get Order History", "GET", "api/orders/history", params={"limit": 20})
    
    # 10. Test Place Order
    order_data = {
        "coin": "BTC",
        "is_buy": True,
        "sz": 0.1,
        "limit_px": 50000,
        "order_type": "limit",
        "time_in_force": "Gtc",
        "reduce_only": False
    }
    success, order_response = tester.run_test("Place Order", "POST", "api/orders", data=order_data)
    
    # 11. Test Cancel Order (if previous test succeeded)
    if success and "data" in order_response and "oid" in order_response["data"]:
        order_id = order_response["data"]["oid"]
        coin = order_response["data"]["coin"]
        tester.run_test("Cancel Order", "DELETE", f"api/orders/{coin}/{order_id}")
    
    # 12. Test Strategies Endpoints
    tester.run_test("Get Strategies", "GET", "api/strategies")
    
    # 13. Test Create Strategy
    strategy_data = {
        "name": "Test Strategy",
        "description": "A test strategy created by API test",
        "coin": "BTC",
        "status": "active",
        "config": {
            "entry_conditions": {"indicator": "MA", "period": 20, "condition": "crossover"},
            "exit_conditions": {"indicator": "RSI", "period": 14, "threshold": 70},
            "risk_management": {"stop_loss": 0.05, "take_profit": 0.1},
            "position_sizing": {"type": "fixed", "size": 0.1}
        }
    }
    success, strategy_response = tester.run_test("Create Strategy", "POST", "api/strategies", data=strategy_data)
    
    # 14. Test Update Strategy (if previous test succeeded)
    if success and "data" in strategy_response and "id" in strategy_response["data"]:
        strategy_id = strategy_response["data"]["id"]
        strategy_data["description"] = "Updated test strategy"
        tester.run_test("Update Strategy", "PUT", f"api/strategies/{strategy_id}", data=strategy_data)
        
        # 15. Test Delete Strategy
        tester.run_test("Delete Strategy", "DELETE", f"api/strategies/{strategy_id}")
    
    # 16. Test Settings Endpoints
    tester.run_test("Get Settings", "GET", "api/settings")
    
    # 17. Test API Status
    tester.run_test("Get API Status", "GET", "api/settings/api-status")
    
    # 18. Test Available Coins
    tester.run_test("Get Available Coins", "GET", "api/coins")
    
    # Print summary
    tester.print_summary()
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
