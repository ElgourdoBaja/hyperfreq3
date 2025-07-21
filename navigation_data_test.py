import requests
import sys
import json
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url="https://54bf5074-fbbb-49dd-a379-2b55c68d8cb8.preview.emergentagent.com"):
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
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)[:500]}...")
                    result = {
                        "name": name,
                        "status": "PASSED",
                        "response": response_data
                    }
                    self.test_results.append(result)
                    return success, response_data
                except:
                    print(f"Response: {response.text[:200]}...")
                    result = {
                        "name": name,
                        "status": "PASSED",
                        "response": response.text
                    }
                    self.test_results.append(result)
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                result = {
                    "name": name,
                    "status": "FAILED",
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "response": response.text
                }
                self.test_results.append(result)
                return False, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "name": name,
                "status": "ERROR",
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_health_endpoint(self):
        """Test the health endpoint"""
        return self.run_test("Health Check", "GET", "api/health")

    def test_portfolio_endpoint(self):
        """Test the portfolio endpoint - should show real account data"""
        success, response = self.run_test("Portfolio Data", "GET", "api/portfolio")
        
        if success:
            # Verify real data is being returned
            data = response.get("data", {})
            positions = data.get("positions", [])
            
            # Check if the account value is real (likely 0.0 for new account)
            account_value = data.get("account_value", None)
            if account_value is not None:
                print(f"✅ Account value is present: {account_value}")
            else:
                print("❌ Account value is missing")
                success = False
            
            # Check if positions are real (should be empty or real positions, not mock data)
            if isinstance(positions, list):
                print(f"✅ Positions data is a list with {len(positions)} items")
                
                # Check for mock data (BTC/ETH positions that shouldn't be there)
                mock_positions = [p for p in positions if p.get("coin") in ["BTC", "ETH"] and p.get("size", 0) > 0]
                if mock_positions:
                    print("❌ Found mock positions that shouldn't be there:")
                    for pos in mock_positions:
                        print(f"  - {pos.get('coin')}: {pos.get('size')} (PnL: {pos.get('unrealized_pnl')})")
                    success = False
                else:
                    print("✅ No mock positions found")
            else:
                print("❌ Positions data is not a list")
                success = False
                
        return success, response

    def test_account_endpoint(self):
        """Test the account endpoint - should show real account data"""
        success, response = self.run_test("Account Info", "GET", "api/account")
        
        if success:
            # Verify real data is being returned
            data = response.get("data", {})
            
            # Check for the real account address
            wallet_address = data.get("wallet_address", "")
            expected_address = "0xc00Ee5EAfE510c41f12CFed2ADD73Ef49A6F845a"
            
            if wallet_address == expected_address:
                print(f"✅ Correct wallet address found: {wallet_address}")
            else:
                print(f"❌ Wrong wallet address: {wallet_address}, expected: {expected_address}")
                success = False
            
            # Check for real balance values (likely 0.0 for new account)
            available_balance = data.get("available_balance", None)
            if available_balance is not None:
                print(f"✅ Available balance is present: {available_balance}")
            else:
                print("❌ Available balance is missing")
                success = False
                
        return success, response

    def test_market_data_endpoint(self, coin="BTC"):
        """Test the market data endpoint - should show real market data"""
        success, response = self.run_test(f"Market Data for {coin}", "GET", f"api/market/{coin}")
        
        if success:
            # Verify real market data is being returned
            data = response.get("data", {})
            
            # Check for essential market data fields
            required_fields = ["price", "24h_change", "24h_volume", "24h_high", "24h_low"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print(f"✅ All required market data fields are present")
                print(f"  - Current price: {data.get('price')}")
                print(f"  - 24h change: {data.get('24h_change')}")
            else:
                print(f"❌ Missing required market data fields: {', '.join(missing_fields)}")
                success = False
                
        return success, response

    def test_settings_api_status(self):
        """Test the API status endpoint - should show successful connection"""
        success, response = self.run_test("API Status", "GET", "api/settings/api-status")
        
        if success:
            data = response.get("data", {})
            
            # Check if API is configured
            is_configured = data.get("is_configured", False)
            if is_configured:
                print("✅ API is correctly configured")
            else:
                print("❌ API is not configured")
                success = False
            
            # Check test result message
            test_result = data.get("test_result", "")
            if "✅" in test_result and "successful" in test_result:
                print(f"✅ API connection is successful: '{test_result}'")
            else:
                print(f"❌ API connection is not successful: '{test_result}'")
                success = False
            
            # Check wallet address
            wallet_address = data.get("wallet_address", "")
            if wallet_address and "0x" in wallet_address:
                print(f"✅ Wallet address is present: {wallet_address}")
            else:
                print("❌ Wallet address is missing or invalid")
                success = False
                
        return success, response

    def run_all_tests(self):
        """Run all tests and print a summary"""
        print("\n🚀 Starting Hypertrader API Tests for Navigation and Real Data...")
        
        # Test health endpoint
        self.test_health_endpoint()
        
        # Test portfolio endpoint
        self.test_portfolio_endpoint()
        
        # Test account endpoint
        self.test_account_endpoint()
        
        # Test market data endpoint
        self.test_market_data_endpoint("BTC")
        self.test_market_data_endpoint("ETH")
        
        # Test API status
        self.test_settings_api_status()
        
        # Print summary
        print("\n📊 Test Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run) * 100:.2f}%")
        
        # Print detailed results
        print("\n📋 Detailed Test Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_icon} {result['name']}: {result['status']}")
        
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