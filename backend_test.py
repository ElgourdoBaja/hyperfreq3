
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

    def test_update_settings_with_whitespace(self):
        """Test updating settings with whitespace in fields to verify trimming"""
        print("\n📋 Testing PUT /api/settings with whitespace in fields...")
        
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
        
        # Prepare test data with whitespace in fields
        test_data = current_settings.get("data", {})
        test_data["api_credentials"] = {
            "wallet_address": "  0x1234567890abcdef1234567890abcdef12345678  ",
            "api_key": " test_api_key_123 ",
            "api_secret": "  test_api_secret_456  ",
            "environment": "mainnet",
            "is_configured": True
        }
        
        # Update settings
        success, response = self.run_test(
            "Update Settings with Whitespace",
            "PUT",
            "api/settings",
            200,
            data=test_data
        )
        
        if success:
            print("✅ Successfully updated settings with whitespace in fields")
            
            # Check API status to verify whitespace was trimmed
            _, status_response = self.run_test(
                "Check API Status After Whitespace Update",
                "GET",
                "api/settings/api-status",
                200
            )
            
            is_configured = status_response.get("data", {}).get("is_configured", False)
            if is_configured:
                print("✅ API is correctly configured after whitespace trimming")
            else:
                print("❌ API is not configured after whitespace trimming")
                success = False
                
            # Check credentials status
            creds_status = status_response.get("data", {}).get("credentials_status", {})
            if (creds_status.get("wallet_address") and 
                creds_status.get("api_key") and 
                creds_status.get("api_secret")):
                print("✅ All three credential fields are properly recognized after whitespace trimming")
            else:
                print("❌ Not all credential fields are recognized after whitespace trimming")
                print(f"Credentials status: {creds_status}")
                success = False
        
        return success, response

    def test_api_status_with_all_fields(self):
        """Test the API status endpoint with all fields filled"""
        print("\n📋 Testing API status with all fields filled...")
        
        # First set up all fields
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
            "environment": "mainnet",
            "is_configured": True
        }
        
        # Update settings
        success, _ = self.run_test(
            "Update Settings with All Fields",
            "PUT",
            "api/settings",
            200,
            data=test_data
        )
        
        if not success:
            print("❌ Failed to update settings with all fields")
            return False, {}
        
        # Check API status
        success, response = self.run_test(
            "Get API Status with All Fields",
            "GET",
            "api/settings/api-status",
            200
        )
        
        if success:
            data = response.get("data", {})
            
            # Check if API is configured
            if data.get("is_configured"):
                print("✅ API is correctly configured with all fields filled")
            else:
                print("❌ API is not configured even with all fields filled")
                success = False
            
            # Check environment
            if data.get("environment") == "mainnet":
                print("✅ Environment is correctly set to mainnet")
            else:
                print(f"❌ Environment is not correctly set: {data.get('environment')}")
                success = False
            
            # Check credentials status
            creds_status = data.get("credentials_status", {})
            if (creds_status.get("wallet_address") and 
                creds_status.get("api_key") and 
                creds_status.get("api_secret")):
                print("✅ All three credential fields are properly recognized")
            else:
                print("❌ Not all credential fields are recognized")
                print(f"Credentials status: {creds_status}")
                success = False
            
            # Check test result message
            test_result = data.get("test_result", "")
            if "✅" in test_result and "successful" in test_result:
                print(f"✅ Test result shows success: '{test_result}'")
            else:
                print(f"❌ Test result does not show success: '{test_result}'")
                success = False
        
        return success, response

    def test_auto_refresh_behavior(self):
        """Test that API status is automatically refreshed after saving settings"""
        print("\n📋 Testing auto-refresh behavior after saving settings...")
        
        # First set up with missing fields
        _, current_settings = self.run_test(
            "Get Current Settings",
            "GET",
            "api/settings",
            200
        )
        
        if not current_settings:
            print("❌ Could not get current settings to update")
            return False, {}
        
        # Prepare test data with missing fields
        test_data = current_settings.get("data", {})
        test_data["api_credentials"] = {
            "wallet_address": "",
            "api_key": "",
            "api_secret": "",
            "environment": "mainnet"
        }
        
        # Update settings to unconfigured state
        success, _ = self.run_test(
            "Update Settings to Unconfigured State",
            "PUT",
            "api/settings",
            200,
            data=test_data
        )
        
        if not success:
            print("❌ Failed to update settings to unconfigured state")
            return False, {}
        
        # Verify unconfigured state
        _, status_before = self.run_test(
            "Verify Unconfigured State",
            "GET",
            "api/settings/api-status",
            200
        )
        
        if status_before.get("data", {}).get("is_configured"):
            print("❌ API is still showing as configured when it should not be")
            return False, {}
        
        # Now update with all fields
        test_data["api_credentials"] = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "api_key": "test_api_key_123",
            "api_secret": "test_api_secret_456",
            "environment": "mainnet"
        }
        
        success, _ = self.run_test(
            "Update Settings to Configured State",
            "PUT",
            "api/settings",
            200,
            data=test_data
        )
        
        if not success:
            print("❌ Failed to update settings to configured state")
            return False, {}
        
        # Check API status immediately after update
        success, status_after = self.run_test(
            "Check API Status After Update",
            "GET",
            "api/settings/api-status",
            200
        )
        
        if success:
            if status_after.get("data", {}).get("is_configured"):
                print("✅ API status is automatically refreshed to show configured state")
            else:
                print("❌ API status is not showing as configured after update")
                success = False
        
        return success, status_after

    def test_validation_with_whitespace(self):
        """Test validation with whitespace in fields"""
        print("\n📋 Testing validation with whitespace in fields...")
        
        # First get current settings
        _, current_settings = self.run_test(
            "Get Current Settings",
            "GET",
            "api/settings",
            200
        )
        
        if not current_settings:
            print("❌ Could not get current settings for validation test")
            return False, {}
        
        test_cases = [
            {
                "name": "Whitespace only in wallet_address",
                "data": {
                    "wallet_address": "   ",
                    "api_key": "test_api_key_123",
                    "api_secret": "test_api_secret_456",
                    "environment": "mainnet"
                },
                "expected_configured": False
            },
            {
                "name": "Whitespace only in api_key",
                "data": {
                    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                    "api_key": "  ",
                    "api_secret": "test_api_secret_456",
                    "environment": "mainnet"
                },
                "expected_configured": False
            },
            {
                "name": "Whitespace only in api_secret",
                "data": {
                    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                    "api_key": "test_api_key_123",
                    "api_secret": "  ",
                    "environment": "mainnet"
                },
                "expected_configured": False
            },
            {
                "name": "Whitespace padding in all fields",
                "data": {
                    "wallet_address": "  0x1234567890abcdef1234567890abcdef12345678  ",
                    "api_key": "  test_api_key_123  ",
                    "api_secret": "  test_api_secret_456  ",
                    "environment": "mainnet"
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
            success, _ = self.run_test(
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
            "environment": "mainnet",
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
        print("\n🚀 Starting Hyperliquid Settings API Tests for Fixed Issues...")
        
        # Test API status with all fields filled
        self.test_api_status_with_all_fields()
        
        # Test whitespace handling
        self.test_update_settings_with_whitespace()
        
        # Test validation with whitespace
        self.test_validation_with_whitespace()
        
        # Test auto-refresh behavior
        self.test_auto_refresh_behavior()
        
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
