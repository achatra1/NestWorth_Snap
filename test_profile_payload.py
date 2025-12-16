"""Test script to validate profile payload structure."""
import json
from backend.models.profile import FinancialProfileCreate

# This is the payload structure sent from the frontend
test_payload = {
    "partner1Income": 5000.0,
    "partner2Income": 4500.0,
    "zipCode": "10001",
    "dueDate": "2026-04-15",
    "currentSavings": 10000.0,
    "numberOfChildren": 1,
    "childcarePreference": "daycare",
    "partner1Leave": {
        "durationWeeks": 12,
        "percentPaid": 100
    },
    "partner2Leave": {
        "durationWeeks": 12,
        "percentPaid": 60
    },
    "monthlyHousingCost": 2000.0,
    "monthlyCreditCardExpenses": 500.0
}

print("Testing profile payload validation...")
print(f"Payload: {json.dumps(test_payload, indent=2)}")

try:
    profile = FinancialProfileCreate(**test_payload)
    print("\n✓ Validation successful!")
    print(f"Profile: {profile}")
except Exception as e:
    print(f"\n✗ Validation failed: {e}")
    print(f"Error type: {type(e).__name__}")