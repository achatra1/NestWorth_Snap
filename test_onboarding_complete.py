"""Test complete onboarding flow with profile save."""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_onboarding_flow():
    """Test the complete onboarding flow."""
    
    # Step 1: Register a new user
    print("Step 1: Registering new user...")
    register_data = {
        "email": f"test_onboarding_{hash('test')}@example.com",
        "name": "Test User",
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=register_data)
    print(f"Registration status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"Registration failed: {response.text}")
        return False
    
    auth_data = response.json()
    token = auth_data["token"]
    user_id = auth_data["user"]["id"]
    print(f"✓ User registered successfully with ID: {user_id}")
    
    # Step 2: Create profile (simulating onboarding completion)
    print("\nStep 2: Creating profile...")
    profile_data = {
        "partner1Income": 5000.0,
        "partner2Income": 4500.0,
        "zipCode": "10001",
        "dueDate": "2026-04-15",
        "currentSavings": 10000.0,
        "childcarePreference": "daycare",
        "partner1Leave": {
            "durationWeeks": 12,
            "percentPaid": 100
        },
        "partner2Leave": {
            "durationWeeks": 12,
            "percentPaid": 60
        },
        "monthlyHousingCost": 2000.0
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/profiles", json=profile_data, headers=headers)
    print(f"Profile creation status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"Profile creation failed: {response.text}")
        return False
    
    profile = response.json()
    print(f"✓ Profile created successfully")
    print(f"Profile data: {json.dumps(profile, indent=2)}")
    
    # Step 3: Verify profile can be retrieved
    print("\nStep 3: Retrieving profile...")
    response = requests.get(f"{BASE_URL}/profiles/me", headers=headers)
    print(f"Profile retrieval status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Profile retrieval failed: {response.text}")
        return False
    
    retrieved_profile = response.json()
    print(f"✓ Profile retrieved successfully")
    print(f"Retrieved profile matches: {profile['id'] == retrieved_profile['id']}")
    
    print("\n✅ All tests passed! Onboarding flow is working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_onboarding_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)