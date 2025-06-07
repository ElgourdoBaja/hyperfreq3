
import requests
import json
import sys
import time

class HyperliquidSettingsTest:
    def __init__(self, base_url):
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
                result = {
                    "name": name,
                    "status": "PASSED",
                    "response": response.json() if response.text else {}
                }
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                result = {
                    "name": name,
                    "status": "FAILED",
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "response": response.json() if response.text else {}
                }
            
            self.test_results.append(result)
            return success, response.json() if response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "name": name,
                "status": "ERROR",
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_get_settings(self):
        """Test getting current settings"""
        print("\n📋 Testing GET /api/settings endpoint...")
        success, response = self.run_test(
            "Get Settings",
            "GET",
            "api/settings",
            200
        )
        
        if success:
            # Verify the response structure
            if "api_credentials" in response.get("data", {}):
                print("✅ Response contains api_credentials field")
                
                # Check if all three required fields are present in the schema
                api_creds = response["data"]["api_credentials"]
                required_fields = ["wallet_address", "api_key", "api_secret"]
                missing_fields = [field for field in required_fields if field not in api_creds]
                
                if not missing_fields:
                    print("✅ All required fields (wallet_address, api_key, api_secret) are present in the schema")
                else:
                    print(f"❌ Missing required fields in schema: {', '.join(missing_fields)}")
            else:
                print("❌ Response does not contain api_credentials field")
        
        return success, response

    def test_update_settings(self):
        """Test updating settings with all three required fields"""
        print("\n📋 Testing PUT /api/settings endpoint...")
        
        # First get current settings
        _, current_settings = self.run_test(
            "Get Current Settings",
            "GET",
            "api/settings",
            200
        )
        
        if not current_settings:
            print("❌ Could not get current settings to update")
            return False, {}
        
        # Prepare test data with all three required fields
        test_data = current_settings.get("data", {})
        test_data["api_credentials"] = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "api_key": "test_api_key_123",
            "api_secret": "test_api_secret_456",
            "environment": "testnet",
            "is_configured": True
        }
        
        # Update settings
        success, response = self.run_test(
            "Update Settings",
            "PUT",
            "api/settings",
            200,
            data=test_data
        )
        
        if success:
            print("✅ Successfully updated settings with all three required fields")
            
            # Verify the updated settings
            verify_success, verify_response = self.run_test(
                "Verify Updated Settings",
                "GET",
                "api/settings",
                200
            )
            
            if verify_success:
                updated_creds = verify_response.get("data", {}).get("api_credentials", {})
                if (updated_creds.get("wallet_address") == "0x1234567890abcdef1234567890abcdef12345678" and
                    updated_creds.get("api_key") == "test_api_key_123" and
                    updated_creds.get("api_secret") == "test_api_secret_456"):
                    print("✅ All three fields were correctly saved and retrieved")
                else:
                    print("❌ Updated settings do not match what was sent")
                    success = False
        
        return success, response

    def test_api_status(self):
        """Test the API status endpoint"""
        print("\n📋 Testing GET /api/settings/api-status endpoint...")
        success, response = self.run_test(
            "Get API Status",
            "GET",
            "api/settings/api-status",
            200
        )
        
        if success:
            # Verify the response structure
            data = response.get("data", {})
            if "is_configured" in data and "environment" in data and "test_result" in data:
                print("✅ API status response contains all required fields")
                
                # Check if wallet_address is included in the response
                if "wallet_address" in data:
                    print("✅ API status includes wallet_address information")
                else:
                    print("❌ API status is missing wallet_address information")
            else:
                print("❌ API status response is missing required fields")
                success = False
        
        return success, response

    def test_validation_requirements(self):
        """Test that all three fields are required for validation"""
        print("\n📋 Testing validation requirements for all three fields...")
        
        # First get current settings
        _, current_settings = self.run_test(
            "Get Current Settings for Validation Test",
            "GET",
            "api/settings",
            200
        )
        
        if not current_settings:
            print("❌ Could not get current settings for validation test")
            return False
        
        test_cases = [
            {
                "name": "Missing wallet_address",
                "data": {
                    "api_key": "test_api_key_123",
                    "api_secret": "test_api_secret_456",
                    "environment": "testnet"
                },
                "expected_configured": False
            },
            {
                "name": "Missing api_key",
                "data": {
                    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                    "api_secret": "test_api_secret_456",
                    "environment": "testnet"
                },
                "expected_configured": False
            },
            {
                "name": "Missing api_secret",
                "data": {
                    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                    "api_key": "test_api_key_123",
                    "environment": "testnet"
                },
                "expected_configured": False
            },
            {
                "name": "All fields present",
                "data": {
                    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                    "api_key": "test_api_key_123",
                    "api_secret": "test_api_secret_456",
                    "environment": "testnet"
                },
                "expected_configured": True
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            print(f"\n🔍 Testing {test_case['name']}...")
            
            # Prepare test data
            test_data = current_settings.get("data", {})
            test_data["api_credentials"] = test_case["data"]
            
            # Update settings
            success, response = self.run_test(
                f"Update Settings - {test_case['name']}",
                "PUT",
                "api/settings",
                200,
                data=test_data
            )
            
            if success:
                # Check API status to see if it's configured
                _, status_response = self.run_test(
                    f"Check API Status - {test_case['name']}",
                    "GET",
                    "api/settings/api-status",
                    200
                )
                
                is_configured = status_response.get("data", {}).get("is_configured", False)
                if is_configured == test_case["expected_configured"]:
                    print(f"✅ {test_case['name']}: is_configured = {is_configured} (Expected: {test_case['expected_configured']})")
                else:
                    print(f"❌ {test_case['name']}: is_configured = {is_configured} (Expected: {test_case['expected_configured']})")
                    all_passed = False
            else:
                all_passed = False
        
        # Reset to a valid configuration
        test_data = current_settings.get("data", {})
        test_data["api_credentials"] = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "api_key": "test_api_key_123",
            "api_secret": "test_api_secret_456",
            "environment": "testnet",
            "is_configured": True
        }
        
        self.run_test(
            "Reset to Valid Configuration",
            "PUT",
            "api/settings",
            200,
            data=test_data
        )
        
        return all_passed

    def run_all_tests(self):
        """Run all tests and print a summary"""
        print("\n🚀 Starting Hyperliquid Settings API Tests...")
        
        # Test getting settings
        self.test_get_settings()
        
        # Test updating settings
        self.test_update_settings()
        
        # Test API status
        self.test_api_status()
        
        # Test validation requirements
        self.test_validation_requirements()
        
        # Print summary
        print("\n📊 Test Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run) * 100:.2f}%")
        
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://675a754d-13da-4f9c-b1c7-a10e6ab42a32.preview.emergentagent.com"
    
    # Run the tests
    tester = HyperliquidSettingsTest(backend_url)
    success = tester.run_all_tests()
    
    # Return exit code based on test results
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
