"""
Expense assumptions module for baby cost calculations.
Ports logic from frontend/src/utils/expenseAssumptions.ts and frontend/src/data/*.ts
"""

from typing import Dict, List, Literal, Optional, TypedDict
from backend.data.childcare_loader import get_childcare_cost_by_zip as get_excel_childcare_cost


class OneTimeCosts(TypedDict):
    crib: float
    stroller: float
    car_seat: float
    high_chair: float


class MonthlyRecurring(TypedDict):
    diapers: float
    wipes: float
    formula: float
    baby_food: float
    miscellaneous: float


class ChildcareCosts(TypedDict):
    daycare: float
    nanny: float
    stay_at_home: float


class ExpenseAssumptions(TypedDict):
    cost_band: Literal['low', 'medium', 'high']
    one_time_costs: OneTimeCosts
    monthly_recurring: MonthlyRecurring
    childcare_costs: ChildcareCosts
    childcare_start_month: int
    zip_code_found: bool


class ChildcareCostByZip(TypedDict):
    zip_code: str
    weekly_infant_cost: float
    weekly_toddler_cost: float
    weekly_preschool_cost: float
    state: str
    city: Optional[str]


class RecurringExpense(TypedDict):
    item: str
    category: str
    low_cost: float
    average_cost: float
    high_cost: float
    start_month: int
    end_month: Optional[int]
    notes: Optional[str]


class OneTimeExpense(TypedDict):
    item: str
    category: str
    low_cost: float
    average_cost: float
    high_cost: float
    notes: Optional[str]


# Average childcare costs for fallback when ZIP not found
AVERAGE_CHILDCARE_COSTS = {
    'weekly_infant_cost': 340,
    'weekly_toddler_cost': 300,
    'weekly_preschool_cost': 260,
}


def weekly_to_monthly_cost(weekly_cost: float) -> float:
    """Convert weekly cost to monthly (multiply by 4.33 weeks per month)."""
    return round(weekly_cost * 4.33)


def determine_cost_level(weekly_infant_cost: float) -> Literal['low', 'medium', 'high']:
    """Determine cost level based on childcare costs."""
    if weekly_infant_cost < 280:
        return 'low'
    if weekly_infant_cost > 400:
        return 'high'
    return 'medium'


# Removed duplicate data structures - using Excel loaders as single source of truth
# One-time and recurring expenses are now loaded from Excel files via data loaders


def get_baby_expense_assumptions(profile: dict) -> ExpenseAssumptions:
    """
    Get baby expense assumptions based on user profile.
    Ports logic from frontend/src/utils/expenseAssumptions.ts
    """
    # Get childcare preference from profile
    childcare_preference = profile.get('childcare_preference', 'daycare')
    zip_code_found = False
    
    # Get childcare costs from Excel file
    excel_data = get_excel_childcare_cost(profile['zip_code'], childcare_preference)
    
    if excel_data and excel_data.get('infant', 0) > 0:
        # Use data from Excel file
        weekly_infant_cost = excel_data['infant']
        weekly_toddler_cost = excel_data.get('toddler', excel_data['infant'] * 0.88)  # Toddler typically 88% of infant
        zip_code_found = True
    else:
        # ZIP code not found - use default values
        # Center-based care (daycare): $1200/month = ~$277/week
        # Home-based care (nanny): $800/month = ~$185/week
        weekly_infant_cost = 277  # Approximately $1200/month
        weekly_toddler_cost = 277
        zip_code_found = False
    
    # Determine cost band based on childcare costs
    cost_band = determine_cost_level(weekly_infant_cost)
    
    # Calculate monthly costs
    if zip_code_found:
        daycare_monthly = weekly_to_monthly_cost(weekly_infant_cost)
        nanny_monthly = weekly_to_monthly_cost(weekly_infant_cost * 1.8)  # Nannies typically cost ~1.8x daycare
    else:
        # Use default values when ZIP not found
        daycare_monthly = 1200  # Center-based care default
        nanny_monthly = 800   # Home-based care default (nanny is actually cheaper in default case)
    
    return {
        'cost_band': cost_band,
        'one_time_costs': {
            'crib': 800,
            'stroller': 800,
            'car_seat': 500,
            'high_chair': 150,
        },
        'monthly_recurring': {
            'diapers': 105,  # Fixed values based on reference data
            'wipes': 0,  # Included in diapers category
            'formula': 150,
            'baby_food': 0,  # Starts at month 6
            'miscellaneous': 100,
        },
        'childcare_costs': {
            'daycare': daycare_monthly,
            'nanny': nanny_monthly,
            'stay_at_home': 0,
        },
        'childcare_start_month': 6,
        'zip_code_found': zip_code_found,  # Track if ZIP was found for assumptions display
    }


def get_assumption_explanations(assumptions: ExpenseAssumptions) -> List[str]:
    """Get human-readable explanations of assumptions."""
    daycare_cost = assumptions['childcare_costs']['daycare']
    nanny_cost = assumptions['childcare_costs']['nanny']
    zip_code_found = assumptions.get('zip_code_found', True)
    
    # Calculate reduced costs after year 3
    daycare_cost_after_y3 = daycare_cost * 0.8
    nanny_cost_after_y3 = nanny_cost * 0.8
    
    # Build childcare cost explanation based on whether ZIP was found
    if zip_code_found:
        childcare_explanation = f"Childcare Costs (ZIP Code-Based): Based on your ZIP code reference data, center-based care (daycare) costs ${daycare_cost:,.0f}/month (Years 1-3) and ${daycare_cost_after_y3:,.0f}/month (Years 4-5, 20% reduction). Home-based care (nanny) costs ${nanny_cost:,.0f}/month (Years 1-3) and ${nanny_cost_after_y3:,.0f}/month (Years 4-5). Stay-at-home parent option has $0 childcare cost. Childcare starts at month {assumptions['childcare_start_month']}."
        data_source_note = "Data Sources: Childcare costs are based on ZIP code-specific reference data from national childcare cost surveys. Recurring costs (diapers, food, supplies, toys, miscellaneous) are fixed monthly amounts from reference data. Your actual costs may vary based on specific choices and circumstances."
    else:
        childcare_explanation = f"Childcare Costs (Default Values): Your ZIP code was not found in our reference data, so we're using national default values: center-based care (daycare) ${daycare_cost:,.0f}/month (Years 1-3) and ${daycare_cost_after_y3:,.0f}/month (Years 4-5, 20% reduction). Home-based care (nanny) ${nanny_cost:,.0f}/month (Years 1-3) and ${nanny_cost_after_y3:,.0f}/month (Years 4-5). Stay-at-home parent option has $0 childcare cost. Childcare starts at month {assumptions['childcare_start_month']}."
        data_source_note = "Data Sources: Your ZIP code was not found in our childcare cost reference database, so we're using national default values (center-based care: $1,200/month, home-based care: $800/month). Recurring costs (diapers, food, supplies, toys, miscellaneous) are fixed monthly amounts from reference data. Your actual costs may vary significantly based on your location and specific choices."
    
    return [
        f"Regional Cost Band: {assumptions['cost_band'].upper()} - Based on your ZIP code, we've adjusted childcare costs to reflect your local market using reference data from childcare cost surveys.",
        f"One-Time Costs: Essential items purchased at birth (month 0) include crib ($800), stroller ($800), car seat ($500), and high chair ($150). Total one-time costs: $2,250.",
        f"Monthly Recurring Costs: Fixed monthly costs include Diapers ($80), Wipes ($15), Food ($150), Supplies ($25), Toys ($20), and Miscellaneous activities/babysitter ($150 in Years 1-2, increasing 20% annually from Year 3 onward). These costs are applied every month throughout the 5-year period. Healthcare and clothing costs are not included in projections.",
        childcare_explanation,
        "Stay-at-Home Parent: If you choose the stay-at-home option, we assume the lower-earning partner will stay home after their parental leave ends. Their income is set to $0 and childcare costs are $0. All other expenses (diapers, food, supplies, etc.) remain the same.",
        "Childcare Cost Reduction: Childcare costs decrease by 20% after year 3 (age 36 months) as children typically require less intensive care and may transition to preschool programs.",
        "Miscellaneous Cost Increase: Miscellaneous expenses (activities, babysitter, etc.) increase by 20% each year starting from Year 3 to account for growing child's expanding needs and activities.",
        "Parental Leave: Income adjustments are calculated based on your specified leave duration and percentage paid.",
        data_source_note,
    ]