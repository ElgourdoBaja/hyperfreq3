
import requests
import sys
import json
import time
from datetime import datetime

class HypertraderAPITester:
    def __init__(self, base_url="https://675a754d-13da-4f9c-b1c7-a10e6ab42a32.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
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
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_settings(self):
        """Test getting settings"""
        return self.run_test(
            "Get Settings",
            "GET",
            "api/settings",
            200
        )

    def test_update_settings(self, settings_data):
        """Test updating settings"""
        return self.run_test(
            "Update Settings",
            "PUT",
            "api/settings",
            200,
            data=settings_data
        )

    def test_api_status(self):
        """Test API status endpoint"""
        return self.run_test(
            "API Status Check",
            "GET",
            "api/settings/api-status",
            200
        )

    def test_api_status_with_invalid_credentials(self):
        """Test API status with invalid credentials"""
        # First update settings with invalid credentials
        invalid_settings = {
            "api_credentials": {
                "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                "api_secret": "invalid_secret_key",
                "environment": "mainnet",
                "is_configured": True
            }
        }
        
        update_success, _ = self.test_update_settings(invalid_settings)
        if not update_success:
            print("❌ Failed to update settings with invalid credentials")
            return False, {}
        
        # Give the server a moment to process the settings update
        time.sleep(1)
        
        # Now test the API status
        return self.run_test(
            "API Status with Invalid Credentials",
            "GET",
            "api/settings/api-status",
            200
        )

    def test_api_status_with_empty_credentials(self):
        """Test API status with empty credentials"""
        # First update settings with empty credentials
        empty_settings = {
            "api_credentials": {
                "wallet_address": "",
                "api_secret": "",
                "environment": "mainnet",
                "is_configured": False
            }
        }
        
        update_success, _ = self.test_update_settings(empty_settings)
        if not update_success:
            print("❌ Failed to update settings with empty credentials")
            return False, {}
        
        # Give the server a moment to process the settings update
        time.sleep(1)
        
        # Now test the API status
        return self.run_test(
            "API Status with Empty Credentials",
            "GET",
            "api/settings/api-status",
            200
        )

def main():
    # Setup
    tester = HypertraderAPITester()
    
    # Run tests
    print("\n🚀 Starting Hypertrader 1.5 Settings API Tests\n")
    
    # Test 1: Get current settings
    get_success, settings_data = tester.test_get_settings()
    if get_success:
        print(f"Current settings: {json.dumps(settings_data, indent=2)}")
    
    # Test 2: Check API status with current settings
    status_success, status_data = tester.test_api_status()
    if status_success:
        print(f"API Status: {json.dumps(status_data, indent=2)}")
    
    # Test 3: Test with invalid credentials
    invalid_success, invalid_data = tester.test_api_status_with_invalid_credentials()
    if invalid_success:
        print(f"API Status with invalid credentials: {json.dumps(invalid_data, indent=2)}")
    
    # Test 4: Test with empty credentials
    empty_success, empty_data = tester.test_api_status_with_empty_credentials()
    if empty_success:
        print(f"API Status with empty credentials: {json.dumps(empty_data, indent=2)}")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
