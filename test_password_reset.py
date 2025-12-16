"""Test script for password reset functionality."""
import requests
import time

API_BASE_URL = "http://localhost:8000"

def test_password_reset_flow():
    """Test the complete password reset flow."""
    
    print("=" * 60)
    print("Testing Password Reset Flow")
    print("=" * 60)
    
    # Step 1: Create a test user
    print("\n1. Creating test user...")
    signup_data = {
        "email": "resettest@example.com",
        "name": "Reset Test User",
        "password": "oldpassword123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/signup", json=signup_data)
    if response.status_code == 201:
        print("✓ User created successfully")
        user_data = response.json()
        print(f"  User ID: {user_data['user']['id']}")
    elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
        print("✓ User already exists (using existing user)")
    else:
        print(f"✗ Failed to create user: {response.status_code}")
        print(f"  Response: {response.json()}")
        return
    
    # Step 2: Request password reset
    print("\n2. Requesting password reset...")
    reset_request = {"email": "resettest@example.com"}
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/forgot-password", json=reset_request)
    
    if response.status_code == 200:
        print("✓ Password reset requested successfully")
        print(f"  Message: {response.json()['message']}")
    else:
        print(f"✗ Failed to request reset: {response.status_code}")
        print(f"  Response: {response.json()}")
        return
    
    # Step 3: Get the reset token from database (in production, this would be in an email)
    print("\n3. Retrieving reset token from database...")
    from backend.database import get_database
    import asyncio
    
    async def get_token():
        db = get_database()
        user = await db.users.find_one({"email": "resettest@example.com"})
        return user.get("reset_token") if user else None
    
    token = asyncio.run(get_token())
    
    if token:
        print(f"✓ Reset token retrieved: {token[:20]}...")
    else:
        print("✗ No reset token found in database")
        return
    
    # Step 4: Reset password with token
    print("\n4. Resetting password with token...")
    reset_data = {
        "token": token,
        "new_password": "newpassword123"
    }
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/reset-password", json=reset_data)
    
    if response.status_code == 200:
        print("✓ Password reset successfully")
        print(f"  Message: {response.json()['message']}")
    else:
        print(f"✗ Failed to reset password: {response.status_code}")
        print(f"  Response: {response.json()}")
        return
    
    # Step 5: Try logging in with new password
    print("\n5. Testing login with new password...")
    login_data = {
        "email": "resettest@example.com",
        "password": "newpassword123"
    }
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✓ Login successful with new password")
        print(f"  User: {response.json()['user']['name']}")
    else:
        print(f"✗ Failed to login: {response.status_code}")
        print(f"  Response: {response.json()}")
        return
    
    # Step 6: Verify old password no longer works
    print("\n6. Verifying old password no longer works...")
    old_login_data = {
        "email": "resettest@example.com",
        "password": "oldpassword123"
    }
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json=old_login_data)
    
    if response.status_code == 401:
        print("✓ Old password correctly rejected")
    else:
        print(f"✗ Old password still works (should be rejected)")
        return
    
    print("\n" + "=" * 60)
    print("✓ All password reset tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_password_reset_flow()