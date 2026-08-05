import requests
import time

API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_reset_password_flow():
    """Test the complete password reset flow"""
    
    print("=" * 60)
    print("Testing Password Reset Flow")
    print("=" * 60)
    
    # Step 1: Request password reset
    print("\n1. Requesting password reset for test@example.com...")
    response = requests.post(
        f"{API_BASE_URL}/api/v1/auth/forgot-password",
        json={"email": "test@example.com"}
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if "reset_token" in data:
            reset_token = data["reset_token"]
            print(f"\n   ✓ Reset token received: {reset_token[:20]}...")
            
            # Step 2: Verify the reset password URL
            reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
            print(f"\n2. Reset password URL would be:")
            print(f"   {reset_url}")
            
            # Step 3: Test the reset password endpoint
            print(f"\n3. Testing password reset with token...")
            new_password = "NewPassword123!"
            reset_response = requests.post(
                f"{API_BASE_URL}/api/v1/auth/reset-password",
                json={
                    "token": reset_token,
                    "new_password": new_password
                }
            )
            
            print(f"   Status: {reset_response.status_code}")
            print(f"   Response: {reset_response.json()}")
            
            if reset_response.status_code == 200:
                print("\n   ✓ Password reset successful!")
                
                # Step 4: Try to login with new password
                print(f"\n4. Testing login with new password...")
                login_response = requests.post(
                    f"{API_BASE_URL}/api/v1/auth/login",
                    json={
                        "email": "test@example.com",
                        "password": new_password
                    }
                )
                
                print(f"   Status: {login_response.status_code}")
                if login_response.status_code == 200:
                    print("   ✓ Login successful with new password!")
                else:
                    print(f"   ✗ Login failed: {login_response.json()}")
            else:
                print(f"\n   ✗ Password reset failed!")
        else:
            print("\n   ℹ Production mode - email would be sent")
    else:
        print(f"\n   ✗ Failed to request password reset")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_reset_password_flow()