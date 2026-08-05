"""Test script to verify registration API directly"""
import requests
import json

# Test registration endpoint
url = "http://localhost:8000/api/v1/auth/signup"
test_user = {
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPassword123!"
}

print("Testing registration API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(test_user, indent=2)}")
print("\n" + "="*60)

try:
    response = requests.post(url, json=test_user)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")