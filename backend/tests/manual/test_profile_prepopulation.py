"""Test profile prepopulation functionality."""
import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"

def test_profile_prepopulation():
    """Test that profile data can be retrieved and prepopulated."""
    
    # Step 1: Register a new user
    print("Step 1: Registering new user...")
    register_data = {
        "email": f"prepop_test_{hash('test')}@example.com",
        "name": "Prepop Test User",
        "password": "TestPassword123!"
    }
    
    register_response = requests.post(
        f"{API_BASE_URL}/auth/signup",
        json=register_data
    )
    
    if register_response.status_code not in [200, 201]:
        print(f"❌ Registration failed: {register_response.status_code}")
        print(register_response.text)
        return False
    
    token = register_response.json()["token"]
    print("✅ User registered successfully")
    
    # Step 2: Create a profile
    print("\nStep 2: Creating profile...")
    profile_data = {
        "partner1Income": 5000.0,
        "partner2Income": 4500.0,
        "zipCode": "10001",
        "dueDate": "2026-06-15",
        "currentSavings": 15000.0,
        "numberOfChildren": 2,
        "childcarePreference": "daycare",
        "partner1Leave": {
            "durationWeeks": 12,
            "percentPaid": 100
        },
        "partner2Leave": {
            "durationWeeks": 8,
            "percentPaid": 60
        },
        "monthlyHousingCost": 2500.0,
        "monthlyCreditCardExpenses": 800.0
    }
    
    create_response = requests.post(
        f"{API_BASE_URL}/profiles",
        json=profile_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if create_response.status_code != 201:
        print(f"❌ Profile creation failed: {create_response.status_code}")
        print(create_response.text)
        return False
    
    created_profile = create_response.json()
    print("✅ Profile created successfully")
    print(f"Profile ID: {created_profile['id']}")
    
    # Step 3: Retrieve the profile (simulating "Update Profile" click)
    print("\nStep 3: Retrieving profile for prepopulation...")
    get_response = requests.get(
        f"{API_BASE_URL}/profiles/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if get_response.status_code != 200:
        print(f"❌ Profile retrieval failed: {get_response.status_code}")
        print(get_response.text)
        return False
    
    retrieved_profile = get_response.json()
    print("✅ Profile retrieved successfully")
    
    # Step 4: Verify all fields match
    print("\nStep 4: Verifying profile data matches...")
    fields_to_check = [
        "partner1Income", "partner2Income", "zipCode", "dueDate",
        "currentSavings", "numberOfChildren", "childcarePreference",
        "monthlyHousingCost", "monthlyCreditCardExpenses"
    ]
    
    all_match = True
    for field in fields_to_check:
        original = profile_data[field]
        retrieved = retrieved_profile[field]
        
        # Handle date comparison (might be in different formats)
        if field == "dueDate":
            original_date = original.split("T")[0] if "T" in str(original) else original
            retrieved_date = retrieved.split("T")[0] if "T" in str(retrieved) else retrieved
            match = original_date == retrieved_date
        else:
            match = original == retrieved
        
        status = "✅" if match else "❌"
        print(f"{status} {field}: {original} == {retrieved}")
        
        if not match:
            all_match = False
    
    # Check nested leave details
    print("\nChecking partner leave details...")
    for partner in ["partner1Leave", "partner2Leave"]:
        for field in ["durationWeeks", "percentPaid"]:
            original = profile_data[partner][field]
            retrieved = retrieved_profile[partner][field]
            match = original == retrieved
            status = "✅" if match else "❌"
            print(f"{status} {partner}.{field}: {original} == {retrieved}")
            if not match:
                all_match = False
    
    # Step 5: Update the profile with modified data
    print("\nStep 5: Updating profile with new values...")
    updated_data = profile_data.copy()
    updated_data["currentSavings"] = 20000.0  # Changed value
    updated_data["numberOfChildren"] = 3  # Changed value
    
    update_response = requests.post(
        f"{API_BASE_URL}/profiles",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if update_response.status_code != 201:
        print(f"❌ Profile update failed: {update_response.status_code}")
        print(update_response.text)
        return False
    
    updated_profile = update_response.json()
    print("✅ Profile updated successfully")
    
    # Step 6: Verify updates were saved
    print("\nStep 6: Verifying updates were saved...")
    final_response = requests.get(
        f"{API_BASE_URL}/profiles/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    final_profile = final_response.json()
    
    savings_match = final_profile["currentSavings"] == 20000.0
    children_match = final_profile["numberOfChildren"] == 3
    
    print(f"{'✅' if savings_match else '❌'} Current Savings updated: {final_profile['currentSavings']}")
    print(f"{'✅' if children_match else '❌'} Number of Children updated: {final_profile['numberOfChildren']}")
    
    if all_match and savings_match and children_match:
        print("\n🎉 All tests passed! Profile prepopulation works correctly.")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False


if __name__ == "__main__":
    try:
        success = test_profile_prepopulation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)