import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_onboarding_flow():
    """Test the complete onboarding flow from registration to profile creation."""
    
    # Step 1: Register a new user
    print("=" * 60)
    print("STEP 1: Registering new user")
    print("=" * 60)
    
    email = f"onboarding_test_{int(time.time())}@example.com"
    register_data = {
        "email": email,
        "name": "Onboarding Test User",
        "password": "TestPass123!"
    }
    
    register_response = requests.post(f"{API_BASE}/auth/signup", json=register_data)
    print(f"Registration Status: {register_response.status_code}")
    
    if register_response.status_code != 201:
        print(f"Registration failed: {register_response.text}")
        return False
    
    register_result = register_response.json()
    token = register_result["token"]
    user_id = register_result["user"]["id"]
    print(f"✓ User registered successfully")
    print(f"  User ID: {user_id}")
    print(f"  Token: {token[:30]}...")
    
    # Step 2: Verify authentication
    print("\n" + "=" * 60)
    print("STEP 2: Verifying authentication")
    print("=" * 60)
    
    me_response = requests.get(
        f"{API_BASE}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Auth verification status: {me_response.status_code}")
    
    if me_response.status_code != 200:
        print(f"Auth verification failed: {me_response.text}")
        return False
    
    print(f"✓ Authentication verified")
    print(f"  User data: {json.dumps(me_response.json(), indent=2)}")
    
    # Step 3: Create profile (simulating frontend onboarding form)
    print("\n" + "=" * 60)
    print("STEP 3: Creating financial profile")
    print("=" * 60)
    
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
    
    print("Profile data being sent:")
    print(json.dumps(profile_data, indent=2))
    
    profile_response = requests.post(
        f"{API_BASE}/profiles",
        json=profile_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"\nProfile creation status: {profile_response.status_code}")
    
    if profile_response.status_code != 201:
        print(f"✗ Profile creation failed!")
        print(f"  Response: {profile_response.text}")
        try:
            error_detail = profile_response.json()
            print(f"  Error details: {json.dumps(error_detail, indent=2)}")
        except:
            pass
        return False
    
    profile_result = profile_response.json()
    print(f"✓ Profile created successfully")
    print(f"  Profile ID: {profile_result.get('id')}")
    print(f"  Full response:")
    print(json.dumps(profile_result, indent=2))
    
    # Step 4: Retrieve profile
    print("\n" + "=" * 60)
    print("STEP 4: Retrieving profile")
    print("=" * 60)
    
    get_profile_response = requests.get(
        f"{API_BASE}/profiles/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Get profile status: {get_profile_response.status_code}")
    
    if get_profile_response.status_code != 200:
        print(f"✗ Failed to retrieve profile: {get_profile_response.text}")
        return False
    
    retrieved_profile = get_profile_response.json()
    print(f"✓ Profile retrieved successfully")
    print(f"  Retrieved profile:")
    print(json.dumps(retrieved_profile, indent=2))
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✓ All steps completed successfully!")
    print(f"  User: {email}")
    print(f"  User ID: {user_id}")
    print(f"  Profile ID: {profile_result.get('id')}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_onboarding_flow()
        if success:
            print("\n🎉 ONBOARDING FLOW TEST PASSED!")
        else:
            print("\n❌ ONBOARDING FLOW TEST FAILED!")
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()