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
    
    coins_success, coins_data = tester.test_coins()
    if coins_success:
        print(f"Available coins: {len(coins_data.get('data', []))} coins found")
        # Test with top 5 coins
        top_coins = ["BTC", "ETH", "SOL", "AVAX", "MATIC"]
        for coin in top_coins:
            market_success, market_data = tester.test_market_data(coin)
            if market_success:
                price = market_data.get('data', {}).get('price', 'N/A')
                print(f"{coin} price: ${price}")
            
            candlestick_success, _ = tester.test_candlesticks(coin)
            orderbook_success, _ = tester.test_orderbook(coin)
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
