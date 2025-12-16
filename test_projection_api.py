"""Test script for projection calculation API."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_projection_calculation():
    """Test the projection calculation endpoint."""
    
    # Step 1: Login or create a test user
    print("Step 1: Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 401:
        print("User doesn't exist, creating new user...")
        signup_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data)
    
    if response.status_code not in [200, 201]:
        print(f"Login/Signup failed: {response.status_code}")
        print(response.text)
        return
    
    auth_data = response.json()
    token = auth_data["token"]
    print(f"✓ Logged in as {auth_data['user']['name']}")
    
    # Step 2: Create or get profile
    print("\nStep 2: Checking for profile...")
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_response = requests.get(f"{BASE_URL}/api/v1/profiles/me", headers=headers)
    
    if profile_response.status_code == 404:
        print("No profile found, creating one...")
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
        profile_response = requests.post(
            f"{BASE_URL}/api/v1/profiles",
            json=profile_data,
            headers=headers
        )
    
    if profile_response.status_code not in [200, 201]:
        print(f"Profile creation/retrieval failed: {profile_response.status_code}")
        print(profile_response.text)
        return
    
    profile = profile_response.json()
    print(f"✓ Profile ready (ID: {profile.get('id', 'N/A')})")
    
    # Step 3: Calculate projection
    print("\nStep 3: Calculating projection...")
    projection_response = requests.post(
        f"{BASE_URL}/api/v1/projections/calculate",
        json={},
        headers=headers
    )
    
    if projection_response.status_code != 200:
        print(f"Projection calculation failed: {projection_response.status_code}")
        print(projection_response.text)
        return
    
    projection = projection_response.json()
    print("✓ Projection calculated successfully!")
    
    # Step 4: Display key results
    print("\n" + "="*60)
    print("PROJECTION RESULTS")
    print("="*60)
    print(f"5-Year Total Cost: ${projection['totalCost']:,.2f}")
    print(f"Monthly Average: ${projection['totalCost']/60:,.2f}")
    print(f"Ending Savings: ${projection['yearlyProjections'][4]['endingSavings']:,.2f}")
    print(f"Number of Warnings: {len(projection['warnings'])}")
    
    print("\nYear-by-Year Summary:")
    for year in projection['yearlyProjections']:
        print(f"  Year {year['year']}: Income ${year['totalIncome']:,.2f} | "
              f"Expenses ${year['totalExpenses']:,.2f} | "
              f"Net ${year['netCashflow']:,.2f}")
    
    if projection['warnings']:
        print("\nWarnings:")
        for warning in projection['warnings']:
            print(f"  [{warning['severity'].upper()}] {warning['title']}")
            print(f"    {warning['message']}")
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_projection_calculation()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()