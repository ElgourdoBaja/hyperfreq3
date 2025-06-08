
import requests
import sys
import time
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        print(f"Initializing API tester with base URL: {base_url}")

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.status_code != 204:  # No content
                    return success, response.json()
                return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api/health",
            200
        )

    def test_get_coins(self):
        """Test getting available coins"""
        return self.run_test(
            "Get Available Coins",
            "GET",
            "api/coins",
            200
        )

    def test_get_open_orders(self):
        """Test getting open orders"""
        return self.run_test(
            "Get Open Orders",
            "GET",
            "api/orders/open",
            200
        )

    def test_get_market_data(self, coin="SOL"):
        """Test getting market data for a coin"""
        return self.run_test(
            f"Get Market Data for {coin}",
            "GET",
            f"api/market/{coin}",
            200
        )

    def test_cancel_order(self, coin, oid):
        """Test cancelling an order"""
        return self.run_test(
            f"Cancel Order {oid} for {coin}",
            "DELETE",
            f"api/orders/{coin}/{oid}",
            200
        )

def main():
    # Get the backend URL from the frontend .env file
    import os
    
    # Use the REACT_APP_BACKEND_URL from frontend/.env
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1].strip('"\'')
                break
    
    print(f"Using backend URL: {backend_url}")
    
    # Setup tester
    tester = HypertraderAPITester(backend_url)
    
    # Run tests
    print("\n=== Testing Basic API Functionality ===")
    health_success, health_data = tester.test_health_check()
    if not health_success:
        print("❌ Health check failed, stopping tests")
        return 1
    
    print("\n=== Testing Coin Listing ===")
    coins_success, coins_data = tester.test_get_coins()
    if not coins_success:
        print("❌ Coin listing failed, stopping tests")
        return 1
    
    print("\n=== Testing Market Data ===")
    market_success, market_data = tester.test_get_market_data("SOL")
    if not market_success:
        print("❌ Market data failed, stopping tests")
        return 1
    
    print("\n=== Testing Open Orders ===")
    orders_success, orders_data = tester.test_get_open_orders()
    if not orders_success:
        print("❌ Open orders failed, stopping tests")
        return 1
    
    # Check if there's a SOL order with OID 100734659966 to cancel
    sol_order = None
    if orders_success and orders_data.get('success'):
        orders_list = orders_data.get('data', [])
        for order in orders_list:
            if order.get('coin') == 'SOL' and order.get('oid') == 100734659966:
                sol_order = order
                break
    
    if sol_order:
        print(f"\n=== Testing Order Cancellation for SOL Order (OID: 100734659966) ===")
        cancel_success, cancel_data = tester.test_cancel_order('SOL', 100734659966)
        if not cancel_success:
            print("❌ Order cancellation failed")
        else:
            print("✅ Order cancellation successful")
            
            # Verify the order is gone by fetching open orders again
            time.sleep(1)  # Wait a moment for the backend to process
            verify_success, verify_data = tester.test_get_open_orders()
            if verify_success and verify_data.get('success'):
                orders_after = verify_data.get('data', [])
                order_still_exists = any(o.get('oid') == 100734659966 for o in orders_after)
                if order_still_exists:
                    print("❌ Order still exists after cancellation")
                else:
                    print("✅ Order successfully removed after cancellation")
    else:
        print("\n⚠️ No SOL order with OID 100734659966 found to test cancellation")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
