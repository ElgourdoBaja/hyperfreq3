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
                    "status": "PASSED",
                    "response": response.json() if response.headers.get('content-type') == 'application/json' else None
                }
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                result = {
                    "name": name,
                    "status": "FAILED",
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.json() if response.headers.get('content-type') == 'application/json' else None
                }

            self.test_results.append(result)
            return success, response.json() if response.headers.get('content-type') == 'application/json' else None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False, None

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        # Print detailed results for failed tests
        if self.tests_passed < self.tests_run:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result["status"] != "PASSED":
                    print(f"- {result['name']}: {result['status']}")
                    if "error" in result:
                        print(f"  Error: {result['error']}")
                    elif "expected" in result:
                        print(f"  Expected: {result['expected']}, Got: {result['actual']}")
        
        return self.tests_passed == self.tests_run

def test_real_data_integration():
    """Test real data integration in the API"""
    backend_url = "https://675a754d-13da-4f9c-b1c7-a10e6ab42a32.preview.emergentagent.com"
    
    print(f"🚀 Testing Hypertrader API Real Data Integration at: {backend_url}")
    tester = HypertraderAPITester(backend_url)
    
    # Test API health
    tester.run_test("API Health Check", "GET", "api/health", 200)
    
    # Test portfolio endpoint for real data
    success, portfolio_data = tester.run_test("Get Portfolio", "GET", "api/portfolio", 200)
    if success:
        print(f"Portfolio data: Account value: ${portfolio_data['data']['account_value']}")
        print(f"Available balance: ${portfolio_data['data']['available_balance']}")
        print(f"Positions: {len(portfolio_data['data']['positions'])}")
        
        # Check if we're getting real data (empty account with $0.00)
        if portfolio_data['data']['account_value'] == 0.0:
            print("✅ Getting real account data ($0.00 balance)")
        else:
            print(f"❌ Not getting real account data (balance: ${portfolio_data['data']['account_value']})")
        
        # Check if we're getting mock positions
        if len(portfolio_data['data']['positions']) == 0:
            print("✅ No mock positions in portfolio (real data)")
        else:
            print(f"❌ Found {len(portfolio_data['data']['positions'])} positions in portfolio (likely mock data)")
            for pos in portfolio_data['data']['positions']:
                print(f"  - {pos['coin']}: {pos['size']} @ ${pos['entry_price']}")
    
    # Test account info endpoint for real wallet address
    success, account_data = tester.run_test("Get Account Info", "GET", "api/account", 200)
    if success:
        print(f"Account address: {account_data['data']['address']}")
        print(f"Account value: ${account_data['data']['account_value']}")
        
        # Check if we're getting the real wallet address
        expected_address = "0xc00Ee5EAfE510c41f12CFed2ADD73Ef49A6F845a"
        if account_data['data']['address'] == expected_address:
            print(f"✅ Getting real wallet address: {expected_address}")
        else:
            print(f"❌ Not getting real wallet address. Expected: {expected_address}, Got: {account_data['data']['address']}")
    
    # Test API status for connection status
    success, api_status_data = tester.run_test("Get API Status", "GET", "api/settings/api-status", 200)
    if success:
        print(f"API status: {api_status_data['data']['test_result']}")
        print(f"Wallet address: {api_status_data['data']['wallet_address']}")
        
        # Check if API is properly configured
        if api_status_data['data']['is_configured']:
            print("✅ API is properly configured")
            
            # Check if test result shows success
            if "✅" in api_status_data['data']['test_result'] and "successful" in api_status_data['data']['test_result']:
                print(f"✅ API connection test successful: '{api_status_data['data']['test_result']}'")
            else:
                print(f"❌ API connection test not successful: '{api_status_data['data']['test_result']}'")
        else:
            print("❌ API is not properly configured")
    
    # Test market data for real prices
    success, btc_data = tester.run_test("Get BTC Market Data", "GET", "api/market/BTC", 200)
    if success:
        print(f"BTC price: ${btc_data['data']['price']}")
        
        # Check if we're getting real market data (price > 0)
        if btc_data['data']['price'] > 0:
            print("✅ Getting real BTC market data")
        else:
            print("❌ Not getting real BTC market data")
    
    # Print summary
    tester.print_summary()
    
    # Return success status for script
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(test_real_data_integration())