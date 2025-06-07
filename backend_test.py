import requests
import sys
import json
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        print(f"🔍 Testing Hypertrader API at: {self.base_url}")

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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text[:200]}")
                    return False, response.json()
                except:
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health(self):
        """Test health endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "api/health",
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

    def test_candlesticks(self, coin="BTC"):
        """Test candlestick data endpoint"""
        return self.run_test(
            f"Candlestick Data for {coin}",
            "GET",
            f"api/candlesticks/{coin}?interval=1h&limit=50",
            200
        )

    def test_orderbook(self, coin="BTC"):
        """Test orderbook endpoint"""
        return self.run_test(
            f"Order Book for {coin}",
            "GET",
            f"api/orderbook/{coin}",
            200
        )
        
    def test_portfolio(self):
        """Test portfolio endpoint"""
        success, data = self.run_test(
            "Portfolio Data",
            "GET",
            "api/portfolio",
            200
        )
        
        if success:
            portfolio = data.get('data', {})
            account_value = portfolio.get('account_value', 0)
            available_balance = portfolio.get('available_balance', 0)
            positions = portfolio.get('positions', [])
            
            print(f"Account Value: ${account_value}")
            print(f"Available Balance: ${available_balance}")
            print(f"Number of Positions: {len(positions)}")
            
            # Check if account value matches expected value
            if abs(account_value - 135.49) < 1.0:  # Allow for small fluctuations
                print("✅ Account value matches expected ~$135.49")
            else:
                print(f"❌ Account value ${account_value} does not match expected ~$135.49")
                
            # Check if there are no mock positions
            if len(positions) == 0:
                print("✅ No mock positions found")
            else:
                print(f"❌ Found {len(positions)} positions, expected 0")
                for pos in positions:
                    print(f"  - {pos.get('coin')}: Size {pos.get('size')}, Side {pos.get('side')}")
        
        return success, data
        
    def test_account(self):
        """Test account endpoint"""
        success, data = self.run_test(
            "Account Info",
            "GET",
            "api/account",
            200
        )
        
        if success:
            account = data.get('data', {})
            account_value = account.get('account_value', 0)
            withdrawable = account.get('withdrawable', 0)
            wallet_address = account.get('address', '')
            
            print(f"Account Value: ${account_value}")
            print(f"Withdrawable: ${withdrawable}")
            print(f"Wallet Address: {wallet_address}")
            
            # Check if account value matches expected value
            if abs(account_value - 135.49) < 1.0:  # Allow for small fluctuations
                print("✅ Account value matches expected ~$135.49")
            else:
                print(f"❌ Account value ${account_value} does not match expected ~$135.49")
                
            # Check if wallet address matches expected value
            expected_address = "0xa6d83862aD55D6Eb51775c6b2d28b81B011bDB63"
            if wallet_address.lower() == expected_address.lower():
                print("✅ Wallet address matches expected address")
            else:
                print(f"❌ Wallet address {wallet_address} does not match expected {expected_address}")
        
        return success, data
        
    def test_settings(self):
        """Test settings endpoint"""
        success, data = self.run_test(
            "Settings",
            "GET",
            "api/settings",
            200
        )
        
        if success:
            settings = data.get('data', {})
            api_credentials = settings.get('api_credentials', {})
            wallet_address = api_credentials.get('wallet_address', '')
            environment = api_credentials.get('environment', '')
            
            print(f"Wallet Address: {wallet_address}")
            print(f"Environment: {environment}")
            
            # Check if wallet address matches expected value
            expected_address = "0xa6d83862aD55D6Eb51775c6b2d28b81B011bDB63"
            if wallet_address.lower() == expected_address.lower():
                print("✅ Wallet address matches expected address")
            else:
                print(f"❌ Wallet address {wallet_address} does not match expected {expected_address}")
                
            # Check if environment is mainnet
            if environment == "mainnet":
                print("✅ Environment is set to mainnet")
            else:
                print(f"❌ Environment is {environment}, expected mainnet")
        
        return success, data
        
    def test_api_status(self):
        """Test API status endpoint"""
        success, data = self.run_test(
            "API Status",
            "GET",
            "api/settings/api-status",
            200
        )
        
        if success:
            api_status = data.get('data', {})
            is_configured = api_status.get('is_configured', False)
            environment = api_status.get('environment', '')
            test_result = api_status.get('test_result', '')
            wallet_address = api_status.get('wallet_address', '')
            
            print(f"API Configured: {is_configured}")
            print(f"Environment: {environment}")
            print(f"Test Result: {test_result}")
            print(f"Wallet Address: {wallet_address}")
            
            # Check if API is configured
            if is_configured:
                print("✅ API is configured")
            else:
                print("❌ API is not configured")
                
            # Check if test result indicates success
            if "✅" in test_result:
                print("✅ API connection test successful")
            else:
                print(f"❌ API connection test failed: {test_result}")
        
        return success, data
        
    def test_debug_wallet_info(self):
        """Test debug wallet info endpoint"""
        success, data = self.run_test(
            "Debug Wallet Info",
            "GET",
            "api/debug/wallet-info",
            200
        )
        
        if success:
            debug_info = data.get('data', {})
            settings_wallet = debug_info.get('settings_wallet_address', '')
            perp_balance = debug_info.get('hyperliquid_perp_balance', 0)
            spot_balance = debug_info.get('hyperliquid_spot_balance', 0)
            
            print(f"Settings Wallet: {settings_wallet}")
            print(f"Perp Balance: ${perp_balance}")
            print(f"Spot Balance: ${spot_balance}")
            
            # Check if wallet address matches expected value
            expected_address = "0xa6d83862aD55D6Eb51775c6b2d28b81B011bDB63"
            if settings_wallet.lower() == expected_address.lower():
                print("✅ Wallet address matches expected address")
            else:
                print(f"❌ Wallet address {settings_wallet} does not match expected {expected_address}")
                
            # Check if total balance matches expected value
            total_balance = perp_balance + spot_balance
            if abs(total_balance - 135.49) < 1.0:  # Allow for small fluctuations
                print(f"✅ Total balance ${total_balance} matches expected ~$135.49")
            else:
                print(f"❌ Total balance ${total_balance} does not match expected ~$135.49")
        
        return success, data

def main():
    # Get backend URL from frontend .env file
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1].strip('"\'')
                break
    
    print(f"Using backend URL: {backend_url}")
    
    # Setup tester
    tester = HypertraderAPITester(backend_url)
    
    # Run tests
    health_success, health_data = tester.test_health()
    if not health_success:
        print("❌ Health check failed, stopping tests")
        return 1
    
    # Test critical endpoints for account balance verification
    print("\n🔍 TESTING CRITICAL ACCOUNT BALANCE ENDPOINTS:")
    portfolio_success, portfolio_data = tester.test_portfolio()
    account_success, account_data = tester.test_account()
    settings_success, settings_data = tester.test_settings()
    api_status_success, api_status_data = tester.test_api_status()
    debug_success, debug_data = tester.test_debug_wallet_info()
    
    # Test market data endpoints
    print("\n🔍 TESTING MARKET DATA ENDPOINTS:")
    coins_success, coins_data = tester.test_coins()
    if coins_success:
        print(f"Available coins: {len(coins_data.get('data', []))} coins found")
        # Test with top 3 coins
        top_coins = ["BTC", "ETH", "SOL"]
        for coin in top_coins:
            market_success, market_data = tester.test_market_data(coin)
            if market_success:
                price = market_data.get('data', {}).get('price', 'N/A')
                print(f"{coin} price: ${price}")
    
    # Print results
    print("\n📊 BACKEND API TEST RESULTS:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Check if critical tests passed
    critical_tests = [portfolio_success, account_success, api_status_success]
    if all(critical_tests):
        print("✅ All critical account balance endpoints are working")
        
        # Verify the actual balance values
        portfolio_value = portfolio_data.get('data', {}).get('account_value', 0)
        account_value = account_data.get('data', {}).get('account_value', 0)
        
        if abs(portfolio_value - 135.49) < 1.0 and abs(account_value - 135.49) < 1.0:
            print(f"✅ VERIFIED: Real account balance of ~$135.49 is correctly returned by the API")
            print(f"   - Portfolio API: ${portfolio_value}")
            print(f"   - Account API: ${account_value}")
        else:
            print(f"❌ ISSUE: Account balance values don't match expected ~$135.49")
            print(f"   - Portfolio API: ${portfolio_value}")
            print(f"   - Account API: ${account_value}")
    else:
        print("❌ Some critical account balance endpoints failed")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
