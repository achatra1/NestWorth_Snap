"""Test profile creation with actual frontend data format."""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# First, create a test user
print("1. Creating test user...")
signup_data = {
    "email": "profiletest@example.com",
    "name": "Profile Test User",
    "password": "testpass123"
}

response = requests.post(f"{API_BASE}/auth/signup", json=signup_data)
print(f"   Status: {response.status_code}")

if response.status_code == 201:
    data = response.json()
    token = data['token']
    user_id = data['user']['id']
    print(f"   ✓ User created! ID: {user_id}")
    print(f"   Token: {token[:20]}...")
else:
    print(f"   ✗ Failed: {response.json()}")
    exit(1)

# Now try to create a profile with frontend data format
print("\n2. Creating profile with camelCase data...")
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

print(f"   Sending: {json.dumps(profile_data, indent=2)}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.post(f"{API_BASE}/profiles", json=profile_data, headers=headers)
print(f"   Status: {response.status_code}")

if response.status_code == 201:
    saved_profile = response.json()
    print(f"   ✓ Profile created!")
    print(f"   Response: {json.dumps(saved_profile, indent=2)}")
else:
    print(f"   ✗ Failed!")
    print(f"   Response: {response.text}")
    exit(1)

# Verify we can fetch it back
print("\n3. Fetching profile back...")
response = requests.get(f"{API_BASE}/profiles/me", headers=headers)
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    fetched_profile = response.json()
    print(f"   ✓ Profile fetched!")
    print(f"   Response: {json.dumps(fetched_profile, indent=2)}")
else:
    print(f"   ✗ Failed!")
    print(f"   Response: {response.text}")

print("\n" + "="*60)
print("Test Complete")
print("="*60)