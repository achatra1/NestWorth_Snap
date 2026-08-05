"""Test the results page flow with authentication."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_results_flow():
    """Test the complete flow from signup to results."""
    
    # Step 1: Create a test user
    print("Step 1: Creating test user...")
    signup_data = {
        "email": "test_results@example.com",
        "password": "TestPassword123!",
        "name": "Test Results User"
    }
    
    signup_response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data)
    print(f"Signup status: {signup_response.status_code}")
    
    if signup_response.status_code == 201:
        signup_result = signup_response.json()
        token = signup_result["token"]
        print(f"✓ User created, token: {token[:20]}...")
    elif signup_response.status_code == 400:
        # User already exists, try login
        print("User exists, logging in...")
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": signup_data["email"],
            "password": signup_data["password"]
        })
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["token"]
            print(f"✓ Logged in, token: {token[:20]}...")
        else:
            print(f"✗ Login failed: {login_response.text}")
            return
    else:
        print(f"✗ Signup failed: {signup_response.text}")
        return
    
    # Step 2: Create a profile
    print("\nStep 2: Creating profile...")
    profile_data = {
        "partner1Income": 5000,
        "partner2Income": 4500,
        "zipCode": "10001",
        "dueDate": "2025-06-15",
        "currentSavings": 25000,
        "childcarePreference": "daycare",
        "partner1Leave": {
            "durationWeeks": 12,
            "percentPaid": 100
        },
        "partner2Leave": {
            "durationWeeks": 8,
            "percentPaid": 50
        },
        "monthlyHousingCost": 2000
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    profile_response = requests.post(
        f"{BASE_URL}/api/v1/profiles",
        json=profile_data,
        headers=headers
    )
    print(f"Profile creation status: {profile_response.status_code}")
    if profile_response.status_code in [200, 201]:
        print(f"✓ Profile created successfully")
    else:
        print(f"✗ Profile creation failed: {profile_response.text}")
        return
    
    # Step 3: Calculate projection
    print("\nStep 3: Calculating projection...")
    projection_response = requests.post(
        f"{BASE_URL}/api/v1/projections/calculate",
        json={},
        headers=headers
    )
    print(f"Projection calculation status: {projection_response.status_code}")
    
    if projection_response.status_code == 200:
        projection_result = projection_response.json()
        print(f"✓ Projection calculated successfully")
        print(f"  Total cost: ${projection_result.get('totalCost', 0):,.2f}")
        print(f"  Years: {len(projection_result.get('yearlyProjections', []))}")
    else:
        print(f"✗ Projection calculation failed: {projection_response.text}")
        print(f"  Response headers: {dict(projection_response.headers)}")
        return
    
    print("\n✓ All steps completed successfully!")

if __name__ == "__main__":
    test_results_flow()