import requests
import json
import time

# First, let's register and login to get a valid token
API_BASE = "http://localhost:8000/api/v1"

# Register a test user
register_data = {
    "email": f"test_profile_{int(time.time())}@example.com",
    "name": "Test User",
    "password": "TestPass123!"
}

try:
    # Try to register
    import time
    register_data["email"] = f"test_profile_{int(time.time())}@example.com"
    response = requests.post(f"{API_BASE}/auth/signup", json=register_data)
    print(f"Register response: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        token = data["token"]
        print(f"Got token: {token[:20]}...")
        
        # Now try to create a profile
        profile_data = {
            "partner1Income": 5000,
            "partner2Income": 4500,
            "zipCode": "10001",
            "dueDate": "2026-04-15",
            "currentSavings": 10000,
            "childcarePreference": "daycare",
            "partner1Leave": {
                "durationWeeks": 12,
                "percentPaid": 100
            },
            "partner2Leave": {
                "durationWeeks": 12,
                "percentPaid": 60
            },
            "monthlyHousingCost": 2000
        }
        
        print(f"\nSending profile data:")
        print(json.dumps(profile_data, indent=2))
        
        profile_response = requests.post(
            f"{API_BASE}/profiles",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"\nProfile creation response: {profile_response.status_code}")
        print(f"Response body: {profile_response.text}")
        
    else:
        print(f"Registration failed: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")