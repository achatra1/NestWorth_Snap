"""Test script for profile API endpoints."""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_profile_endpoints():
    """Test profile creation and retrieval."""
    
    # First, create a test user and get token
    print("1. Creating test user...")
    signup_data = {
        "email": f"test_profile_{hash('test')}@example.com",
        "name": "Test Profile User",
        "password": "testpass123"
    }
    
    response = requests.post(f"{API_BASE}/auth/signup", json=signup_data)
    if response.status_code != 201:
        print(f"Signup failed: {response.status_code}")
        print(response.text)
        return
    
    auth_data = response.json()
    token = auth_data["token"]
    user_id = auth_data["user"]["id"]
    print(f"✓ User created with ID: {user_id}")
    
    # Test GET /profiles/me before creating profile (should return 404)
    print("\n2. Testing GET /profiles/me (should return 404)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/profiles/me", headers=headers)
    if response.status_code == 404:
        print("✓ Correctly returns 404 when no profile exists")
    else:
        print(f"✗ Expected 404, got {response.status_code}")
        print(response.text)
    
    # Test POST /profiles to create profile
    print("\n3. Creating profile...")
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
    
    response = requests.post(f"{API_BASE}/profiles", json=profile_data, headers=headers)
    if response.status_code == 201:
        saved_profile = response.json()
        print("✓ Profile created successfully")
        print(f"  Profile ID: {saved_profile.get('id')}")
        print(f"  User ID: {saved_profile.get('userId')}")
        print(f"  Partner 1 Income: ${saved_profile.get('partner1Income')}")
        print(f"  ZIP Code: {saved_profile.get('zipCode')}")
    else:
        print(f"✗ Profile creation failed: {response.status_code}")
        print(response.text)
        return
    
    # Test GET /profiles/me after creating profile
    print("\n4. Testing GET /profiles/me (should return profile)...")
    response = requests.get(f"{API_BASE}/profiles/me", headers=headers)
    if response.status_code == 200:
        retrieved_profile = response.json()
        print("✓ Profile retrieved successfully")
        print(f"  Partner 1 Income: ${retrieved_profile.get('partner1Income')}")
        print(f"  Partner 2 Income: ${retrieved_profile.get('partner2Income')}")
        print(f"  ZIP Code: {retrieved_profile.get('zipCode')}")
        print(f"  Childcare Preference: {retrieved_profile.get('childcarePreference')}")
        
        # Verify camelCase fields
        if 'partner1Income' in retrieved_profile and 'zipCode' in retrieved_profile:
            print("✓ Response uses camelCase as expected")
        else:
            print("✗ Response does not use camelCase")
    else:
        print(f"✗ Profile retrieval failed: {response.status_code}")
        print(response.text)
    
    # Test updating profile (POST again with same user)
    print("\n5. Testing profile update...")
    updated_profile_data = profile_data.copy()
    updated_profile_data["partner1Income"] = 5500.0
    updated_profile_data["currentSavings"] = 12000.0
    
    response = requests.post(f"{API_BASE}/profiles", json=updated_profile_data, headers=headers)
    if response.status_code == 201:
        updated_profile = response.json()
        print("✓ Profile updated successfully")
        print(f"  Updated Partner 1 Income: ${updated_profile.get('partner1Income')}")
        print(f"  Updated Current Savings: ${updated_profile.get('currentSavings')}")
    else:
        print(f"✗ Profile update failed: {response.status_code}")
        print(response.text)
    
    print("\n✅ All profile API tests completed!")

if __name__ == "__main__":
    test_profile_endpoints()