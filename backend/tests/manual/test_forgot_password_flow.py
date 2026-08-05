"""Test the forgot password flow with automatic redirect in development mode."""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_forgot_password_with_token():
    """Test that forgot password returns reset_token in development mode."""
    
    # First, create a test user
    print("Creating test user...")
    signup_data = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/signup",
            json=signup_data
        )
        if response.status_code == 201:
            print("✓ Test user created successfully")
        elif response.status_code == 400 and "already registered" in response.text:
            print("✓ Test user already exists")
        else:
            print(f"✗ Failed to create user: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error creating user: {e}")
    
    # Test forgot password endpoint
    print("\nTesting forgot password endpoint...")
    forgot_data = {
        "email": "testuser@example.com"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/forgot-password",
            json=forgot_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Forgot password request successful")
            print(f"  Response: {json.dumps(data, indent=2)}")
            
            if "reset_token" in data and data["reset_token"]:
                print(f"\n✓ SUCCESS: reset_token is present in response (development mode)")
                print(f"  Token: {data['reset_token'][:20]}...")
                print(f"\n✓ Frontend will automatically redirect to:")
                print(f"  /reset-password?token={data['reset_token']}")
                return True
            else:
                print(f"\n✗ FAIL: reset_token not found in response")
                print(f"  This might be production mode or an error")
                return False
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Testing Forgot Password Flow with Auto-Redirect")
    print("="*60)
    success = test_forgot_password_with_token()
    print("\n" + "="*60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("The flow is working correctly in development mode!")
    else:
        print("✗ TESTS FAILED")
    print("="*60)