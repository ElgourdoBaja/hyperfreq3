
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
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

    def test_get_portfolio(self):
        """Test getting portfolio data"""
        return self.run_test(
            "Get Portfolio Data",
            "GET",
            "api/portfolio",
            200
        )

    def test_get_account_info(self):
        """Test getting account information"""
        return self.run_test(
            "Get Account Information",
            "GET",
            "api/account",
            200
        )

    def test_get_settings(self):
        """Test getting user settings"""
        return self.run_test(
            "Get User Settings",
            "GET",
            "api/settings",
            200
        )

    def test_get_api_status(self):
        """Test getting API connection status"""
        return self.run_test(
            "Get API Connection Status",
            "GET",
            "api/settings/api-status",
            200
        )

    def test_get_market_data(self, coin="BTC"):
        """Test getting market data for a coin"""
        return self.run_test(
            f"Get Market Data for {coin}",
            "GET",
            f"api/market/{coin}",
            200
        )

    def test_get_candlestick_data(self, coin="BTC"):
        """Test getting candlestick data for a coin"""
        return self.run_test(
            f"Get Candlestick Data for {coin}",
            "GET",
            f"api/candlesticks/{coin}",
            200
        )

    def test_get_order_book(self, coin="BTC"):
        """Test getting order book for a coin"""
        return self.run_test(
            f"Get Order Book for {coin}",
            "GET",
            f"api/orderbook/{coin}",
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

    def test_get_strategies(self):
        """Test getting strategies"""
        return self.run_test(
            "Get Strategies",
            "GET",
            "api/strategies",
            200
        )

    def test_debug_wallet_info(self):
        """Test debug wallet info endpoint"""
        return self.run_test(
            "Debug Wallet Info",
            "GET",
            "api/debug/wallet-info",
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
    
    print("\n=== Testing Account and Portfolio Data ===")
    # Test account info
    account_success, account_data = tester.test_get_account_info()
    if account_success:
        account_info = account_data.get('data', {})
        print(f"Account Address: {account_info.get('address', 'N/A')}")
        print(f"Account Value: ${account_info.get('account_value', 'N/A')}")
    else:
        print("❌ Account info test failed")
    
    # Test portfolio data
    portfolio_success, portfolio_data = tester.test_get_portfolio()
    if portfolio_success:
        portfolio_info = portfolio_data.get('data', {})
        print(f"Portfolio Account Value: ${portfolio_info.get('account_value', 'N/A')}")
        print(f"Available Balance: ${portfolio_info.get('available_balance', 'N/A')}")
        positions = portfolio_info.get('positions', [])
        print(f"Number of Positions: {len(positions)}")
    else:
        print("❌ Portfolio test failed")
    
    print("\n=== Testing Settings and API Status ===")
    # Test settings
    settings_success, settings_data = tester.test_get_settings()
    if settings_success:
        settings_info = settings_data.get('data', {})
        api_credentials = settings_info.get('api_credentials', {})
        wallet_address = api_credentials.get('wallet_address', 'N/A')
        print(f"Wallet Address: {wallet_address}")
        print(f"Environment: {api_credentials.get('environment', 'N/A')}")
    else:
        print("❌ Settings test failed")
    
    # Test API status
    api_status_success, api_status_data = tester.test_get_api_status()
    if api_status_success:
        api_status_info = api_status_data.get('data', {})
        print(f"API Configured: {api_status_info.get('is_configured', False)}")
        print(f"Test Result: {api_status_info.get('test_result', 'N/A')}")
        print(f"Wallet Address: {api_status_info.get('wallet_address', 'N/A')}")
    else:
        print("❌ API status test failed")
    
    print("\n=== Testing Debug Wallet Info ===")
    debug_success, debug_data = tester.test_debug_wallet_info()
    if debug_success:
        debug_info = debug_data.get('data', {})
        print(f"Settings Wallet Address: {debug_info.get('settings_wallet_address', 'N/A')}")
        print(f"Derived Wallet: {debug_info.get('derived_wallet_from_private_key', 'N/A')}")
        print(f"Perp Balance: ${debug_info.get('hyperliquid_perp_balance', 'N/A')}")
    else:
        print("❌ Debug wallet info test failed")
    
    print("\n=== Testing Market Data ===")
    # Test market data for BTC
    market_success, market_data = tester.test_get_market_data("BTC")
    if not market_success:
        print("❌ Market data test failed")
    
    # Test candlestick data
    candlestick_success, candlestick_data = tester.test_get_candlestick_data("BTC")
    if not candlestick_success:
        print("❌ Candlestick data test failed")
    
    # Test order book
    orderbook_success, orderbook_data = tester.test_get_order_book("BTC")
    if not orderbook_success:
        print("❌ Order book test failed")
    
    print("\n=== Testing Trading Data ===")
    # Test open orders
    orders_success, orders_data = tester.test_get_open_orders()
    if orders_success:
        orders = orders_data.get('data', [])
        print(f"Number of Open Orders: {len(orders)}")
    else:
        print("❌ Open orders test failed")
    
    print("\n=== Testing Strategies ===")
    # Test strategies
    strategies_success, strategies_data = tester.test_get_strategies()
    if strategies_success:
        strategies = strategies_data.get('data', [])
        print(f"Number of Strategies: {len(strategies)}")
    else:
        print("❌ Strategies test failed")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Verify specific requirements from the review request
    print("\n=== VERIFICATION SUMMARY ===")
    wallet_address = None
    account_value = None
    api_connection_status = None
    
    if portfolio_success:
        portfolio_info = portfolio_data.get('data', {})
        account_value = portfolio_info.get('account_value', None)
        print(f"✅ Account Value: ${account_value}")
    else:
        print("❌ Could not verify account value")
    
    if settings_success:
        settings_info = settings_data.get('data', {})
        api_credentials = settings_info.get('api_credentials', {})
        wallet_address = api_credentials.get('wallet_address', None)
        print(f"✅ Wallet Address: {wallet_address}")
    else:
        print("❌ Could not verify wallet address")
    
    if api_status_success:
        api_status_info = api_status_data.get('data', {})
        api_connection_status = api_status_info.get('test_result', None)
        print(f"✅ API Connection Status: {api_connection_status}")
    else:
        print("❌ Could not verify API connection status")
    
    # Check if the real account data is being used
    expected_wallet = "0x78b70c6265F089fd64af7C9b8Fc80e9f371D730A"
    expected_balance = 124.84
    
    if wallet_address and expected_wallet.lower() == wallet_address.lower():
        print(f"✅ VERIFIED: Correct wallet address is being used")
    else:
        print(f"❌ ISSUE: Wallet address mismatch. Expected: {expected_wallet}, Got: {wallet_address}")
    
    if account_value and abs(float(account_value) - expected_balance) < 1.0:  # Allow for small fluctuations
        print(f"✅ VERIFIED: Correct account balance is being used (${account_value})")
    else:
        print(f"❌ ISSUE: Account balance mismatch. Expected: ${expected_balance}, Got: ${account_value}")
    
    if api_connection_status and "successful" in api_connection_status.lower():
        print(f"✅ VERIFIED: API connection is successful")
    else:
        print(f"❌ ISSUE: API connection status issue. Status: {api_connection_status}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
