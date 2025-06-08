
import requests
import sys
import time
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url="https://675a754d-13da-4f9c-b1c7-a10e6ab42a32.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

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
                return success, response.json() if response.text else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health(self):
        """Test API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api/health",
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

    def test_cancel_order(self, coin, oid):
        """Test cancelling an order"""
        return self.run_test(
            f"Cancel Order {coin}/{oid}",
            "DELETE",
            f"api/orders/{coin}/{oid}",
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

def main():
    # Setup
    tester = HypertraderAPITester()
    
    # Run tests
    print("\n===== BACKEND API TESTING =====\n")
    
    # Test API health
    health_success, _ = tester.test_health()
    if not health_success:
        print("❌ API health check failed, stopping tests")
        return 1

    # Test getting market data
    market_success, market_data = tester.test_get_market_data("SOL")
    if market_success:
        print(f"Market data for SOL: Price = ${market_data.get('data', {}).get('price', 'N/A')}")
    
    # Test getting open orders
    orders_success, orders_data = tester.test_get_open_orders()
    if orders_success:
        orders = orders_data.get('data', [])
        if orders:
            print(f"Found {len(orders)} open orders:")
            for order in orders:
                print(f"  - Order ID: {order.get('oid')}, Coin: {order.get('coin')}, Side: {order.get('side')}, Size: {order.get('size')}, Price: {order.get('price')}")
            
            # Test cancelling the first order
            test_order = orders[0]
            cancel_success, cancel_data = tester.test_cancel_order(test_order.get('coin'), test_order.get('oid'))
            if cancel_success:
                print(f"Successfully cancelled order {test_order.get('oid')}")
                
                # Verify order was cancelled by checking open orders again
                time.sleep(1)  # Wait a bit for the cancellation to process
                _, verify_data = tester.test_get_open_orders()
                verify_orders = verify_data.get('data', [])
                
                cancelled_order_still_exists = any(o.get('oid') == test_order.get('oid') for o in verify_orders)
                if not cancelled_order_still_exists:
                    print("✅ Verified order was successfully removed from open orders")
                else:
                    print("❌ Order still appears in open orders after cancellation")
        else:
            print("No open orders found to test cancellation")

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
