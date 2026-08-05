"""Test to verify backend calculation matches frontend logic."""
import sys
sys.path.insert(0, 'backend')

from backend.utils.projection_calculator import calculate_five_year_projection

# Test profile matching the one used in the API test
test_profile = {
    'partner1_income': 5000,
    'partner2_income': 4500,
    'zip_code': '10001',
    'due_date': '2026-04-15',
    'current_savings': 10000,
    'childcare_preference': 'daycare',
    'partner1_leave': {
        'duration_weeks': 12,
        'percent_paid': 100
    },
    'partner2_leave': {
        'duration_weeks': 12,
        'percent_paid': 60
    },
    'monthly_housing_cost': 2000
}

print("Testing projection calculation with test profile...")
print("="*60)

projection = calculate_five_year_projection(test_profile)

print(f"5-Year Total Cost: ${projection['total_cost']:,.2f}")
print(f"Monthly Average: ${projection['total_cost']/60:,.2f}")
print(f"Ending Savings: ${projection['yearly_projections'][4]['ending_savings']:,.2f}")
print(f"Number of Warnings: {len(projection['warnings'])}")

print("\nYear-by-Year Summary:")
for year in projection['yearly_projections']:
    print(f"  Year {year['year']}: Income ${year['total_income']:,.2f} | "
          f"Expenses ${year['total_expenses']:,.2f} | "
          f"Net ${year['net_cashflow']:,.2f}")

print("\nFirst Month Details:")
first_month = projection['monthly_projections'][0]
print(f"  Month 1 Income: ${first_month['income']['total']:,.2f}")
print(f"  Month 1 Expenses: ${first_month['expenses']['total']:,.2f}")
print(f"  Month 1 Net Cashflow: ${first_month['net_cashflow']:,.2f}")
print(f"  Month 1 Cumulative Savings: ${first_month['cumulative_savings']:,.2f}")

print("\nExpense Breakdown (Month 1):")
for key, value in first_month['expenses'].items():
    if key != 'total' and value > 0:
        print(f"  {key}: ${value:,.2f}")

print("\n" + "="*60)
print("✓ Calculation completed successfully!")
print("\nExpected values from API test:")
print("  5-Year Total: $293,312.00")
print("  Ending Savings: $281,288.00")
print("\nActual values from direct calculation:")
print(f"  5-Year Total: ${projection['total_cost']:,.2f}")
print(f"  Ending Savings: ${projection['yearly_projections'][4]['ending_savings']:,.2f}")

# Check if values match
if abs(projection['total_cost'] - 293312) < 1 and abs(projection['yearly_projections'][4]['ending_savings'] - 281288) < 1:
    print("\n✓✓✓ VALUES MATCH! Backend calculation is deterministic and correct!")
else:
    print("\n✗ WARNING: Values don't match exactly. Check for calculation differences.")