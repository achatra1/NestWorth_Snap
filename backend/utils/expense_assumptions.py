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
    clothing: float
    healthcare: float
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


# Childcare costs by ZIP code (sample data from frontend)
CHILDCARE_COSTS_BY_ZIP: List[ChildcareCostByZip] = [
    # High-cost areas
    {'zip_code': '10001', 'weekly_infant_cost': 450, 'weekly_toddler_cost': 400, 'weekly_preschool_cost': 350, 'state': 'NY', 'city': 'New York'},
    {'zip_code': '10002', 'weekly_infant_cost': 445, 'weekly_toddler_cost': 395, 'weekly_preschool_cost': 345, 'state': 'NY', 'city': 'New York'},
    {'zip_code': '94102', 'weekly_infant_cost': 480, 'weekly_toddler_cost': 430, 'weekly_preschool_cost': 380, 'state': 'CA', 'city': 'San Francisco'},
    {'zip_code': '90001', 'weekly_infant_cost': 420, 'weekly_toddler_cost': 370, 'weekly_preschool_cost': 320, 'state': 'CA', 'city': 'Los Angeles'},
    {'zip_code': '98101', 'weekly_infant_cost': 440, 'weekly_toddler_cost': 390, 'weekly_preschool_cost': 340, 'state': 'WA', 'city': 'Seattle'},
    {'zip_code': '02101', 'weekly_infant_cost': 460, 'weekly_toddler_cost': 410, 'weekly_preschool_cost': 360, 'state': 'MA', 'city': 'Boston'},
    {'zip_code': '20001', 'weekly_infant_cost': 430, 'weekly_toddler_cost': 380, 'weekly_preschool_cost': 330, 'state': 'DC', 'city': 'Washington'},
    # Medium-cost areas
    {'zip_code': '60601', 'weekly_infant_cost': 350, 'weekly_toddler_cost': 310, 'weekly_preschool_cost': 270, 'state': 'IL', 'city': 'Chicago'},
    {'zip_code': '75201', 'weekly_infant_cost': 320, 'weekly_toddler_cost': 280, 'weekly_preschool_cost': 240, 'state': 'TX', 'city': 'Dallas'},
    {'zip_code': '30301', 'weekly_infant_cost': 330, 'weekly_toddler_cost': 290, 'weekly_preschool_cost': 250, 'state': 'GA', 'city': 'Atlanta'},
    {'zip_code': '85001', 'weekly_infant_cost': 310, 'weekly_toddler_cost': 270, 'weekly_preschool_cost': 230, 'state': 'AZ', 'city': 'Phoenix'},
    {'zip_code': '33101', 'weekly_infant_cost': 340, 'weekly_toddler_cost': 300, 'weekly_preschool_cost': 260, 'state': 'FL', 'city': 'Miami'},
    # Low-cost areas
    {'zip_code': '35004', 'weekly_infant_cost': 240, 'weekly_toddler_cost': 210, 'weekly_preschool_cost': 180, 'state': 'AL', 'city': 'Birmingham'},
    {'zip_code': '38601', 'weekly_infant_cost': 230, 'weekly_toddler_cost': 200, 'weekly_preschool_cost': 170, 'state': 'MS', 'city': 'Jackson'},
    {'zip_code': '71601', 'weekly_infant_cost': 250, 'weekly_toddler_cost': 220, 'weekly_preschool_cost': 190, 'state': 'AR', 'city': 'Little Rock'},
    {'zip_code': '50301', 'weekly_infant_cost': 260, 'weekly_toddler_cost': 230, 'weekly_preschool_cost': 200, 'state': 'IA', 'city': 'Des Moines'},
]

# Average childcare costs for fallback
AVERAGE_CHILDCARE_COSTS = {
    'weekly_infant_cost': 340,
    'weekly_toddler_cost': 300,
    'weekly_preschool_cost': 260,
}

# One-time expenses data
ONE_TIME_EXPENSES: List[OneTimeExpense] = [
    {'item': 'Crib', 'category': 'Nursery Furniture', 'low_cost': 150, 'average_cost': 300, 'high_cost': 800, 'notes': 'Convertible cribs cost more but last longer'},
    {'item': 'Crib Mattress', 'category': 'Nursery Furniture', 'low_cost': 80, 'average_cost': 150, 'high_cost': 300, 'notes': None},
    {'item': 'Changing Table', 'category': 'Nursery Furniture', 'low_cost': 80, 'average_cost': 120, 'high_cost': 250, 'notes': None},
    {'item': 'Car Seat (Infant)', 'category': 'Transportation', 'low_cost': 100, 'average_cost': 200, 'high_cost': 400, 'notes': 'Rear-facing for infants'},
    {'item': 'Stroller', 'category': 'Transportation', 'low_cost': 100, 'average_cost': 250, 'high_cost': 800, 'notes': 'Travel systems cost more'},
    {'item': 'High Chair', 'category': 'Feeding', 'low_cost': 50, 'average_cost': 150, 'high_cost': 300, 'notes': None},
    {'item': 'Baby Monitor', 'category': 'Safety & Monitoring', 'low_cost': 50, 'average_cost': 100, 'high_cost': 300, 'notes': 'Video monitors cost more'},
    {'item': 'Bottles & Accessories', 'category': 'Feeding', 'low_cost': 50, 'average_cost': 100, 'high_cost': 200, 'notes': None},
]

# Recurring expenses data
RECURRING_EXPENSES: List[RecurringExpense] = [
    # Diapers & Wipes
    {'item': 'Diapers', 'category': 'Diapers & Wipes', 'low_cost': 60, 'average_cost': 80, 'high_cost': 120, 'start_month': 0, 'end_month': 30, 'notes': 'Newborns use 8-12 diapers/day, decreases over time'},
    {'item': 'Wipes', 'category': 'Diapers & Wipes', 'low_cost': 15, 'average_cost': 25, 'high_cost': 40, 'start_month': 0, 'end_month': 36, 'notes': None},
    {'item': 'Diaper Cream', 'category': 'Diapers & Wipes', 'low_cost': 5, 'average_cost': 10, 'high_cost': 20, 'start_month': 0, 'end_month': 30, 'notes': None},
    # Formula & Food
    {'item': 'Formula', 'category': 'Formula & Food', 'low_cost': 100, 'average_cost': 150, 'high_cost': 250, 'start_month': 0, 'end_month': 12, 'notes': 'For formula-fed babies; breastfeeding has minimal cost'},
    {'item': 'Baby Food (Purees)', 'category': 'Formula & Food', 'low_cost': 50, 'average_cost': 80, 'high_cost': 120, 'start_month': 6, 'end_month': 12, 'notes': 'Starts around 6 months'},
    {'item': 'Toddler Food', 'category': 'Formula & Food', 'low_cost': 80, 'average_cost': 120, 'high_cost': 180, 'start_month': 12, 'end_month': None, 'notes': 'Transition to table foods'},
    {'item': 'Snacks', 'category': 'Formula & Food', 'low_cost': 20, 'average_cost': 40, 'high_cost': 60, 'start_month': 9, 'end_month': None, 'notes': None},
    # Clothing
    {'item': 'Clothing (0-12 months)', 'category': 'Clothing', 'low_cost': 30, 'average_cost': 50, 'high_cost': 100, 'start_month': 0, 'end_month': 12, 'notes': 'Babies grow quickly, need frequent size changes'},
    {'item': 'Clothing (12-24 months)', 'category': 'Clothing', 'low_cost': 35, 'average_cost': 60, 'high_cost': 120, 'start_month': 12, 'end_month': 24, 'notes': None},
    {'item': 'Clothing (2-5 years)', 'category': 'Clothing', 'low_cost': 40, 'average_cost': 70, 'high_cost': 140, 'start_month': 24, 'end_month': None, 'notes': None},
    # Healthcare
    {'item': 'Medical Co-pays', 'category': 'Healthcare', 'low_cost': 30, 'average_cost': 50, 'high_cost': 100, 'start_month': 0, 'end_month': None, 'notes': 'Well-child visits, sick visits'},
    {'item': 'Medications & Vitamins', 'category': 'Healthcare', 'low_cost': 10, 'average_cost': 25, 'high_cost': 50, 'start_month': 0, 'end_month': None, 'notes': None},
    {'item': 'Dental Care', 'category': 'Healthcare', 'low_cost': 0, 'average_cost': 20, 'high_cost': 50, 'start_month': 12, 'end_month': None, 'notes': 'First dental visit around 12 months'},
    # Personal Care
    {'item': 'Bath Products', 'category': 'Personal Care', 'low_cost': 10, 'average_cost': 20, 'high_cost': 40, 'start_month': 0, 'end_month': None, 'notes': None},
    {'item': 'Laundry (Extra)', 'category': 'Personal Care', 'low_cost': 15, 'average_cost': 30, 'high_cost': 50, 'start_month': 0, 'end_month': None, 'notes': 'Increased laundry costs'},
    # Toys & Books
    {'item': 'Toys', 'category': 'Toys & Books', 'low_cost': 20, 'average_cost': 40, 'high_cost': 80, 'start_month': 3, 'end_month': None, 'notes': None},
    {'item': 'Books', 'category': 'Toys & Books', 'low_cost': 10, 'average_cost': 20, 'high_cost': 40, 'start_month': 0, 'end_month': None, 'notes': None},
    # Miscellaneous
    {'item': 'Miscellaneous', 'category': 'Miscellaneous', 'low_cost': 50, 'average_cost': 100, 'high_cost': 200, 'start_month': 0, 'end_month': None, 'notes': 'Unexpected expenses, replacements, etc.'},
]

# Essential one-time items
ESSENTIAL_ONE_TIME_ITEMS = [
    'Crib',
    'Crib Mattress',
    'Changing Table',
    'Car Seat (Infant)',
    'Stroller',
    'High Chair',
    'Baby Monitor',
    'Bottles & Accessories',
]


def get_childcare_cost_by_zip(zip_code: str) -> Optional[ChildcareCostByZip]:
    """Get childcare cost data by ZIP code."""
    # Try exact match first
    for cost_data in CHILDCARE_COSTS_BY_ZIP:
        if cost_data['zip_code'] == zip_code:
            return cost_data
    
    # Try matching first 3 digits (ZIP code prefix)
    prefix = zip_code[:3]
    for cost_data in CHILDCARE_COSTS_BY_ZIP:
        if cost_data['zip_code'].startswith(prefix):
            return cost_data
    
    return None


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


def get_essential_one_time_costs(cost_level: Literal['low', 'average', 'high']) -> Dict[str, float]:
    """Get essential one-time costs by cost level."""
    costs = {}
    
    for expense in ONE_TIME_EXPENSES:
        if expense['item'] in ESSENTIAL_ONE_TIME_ITEMS:
            if cost_level == 'low':
                costs[expense['item']] = expense['low_cost']
            elif cost_level == 'high':
                costs[expense['item']] = expense['high_cost']
            else:
                costs[expense['item']] = expense['average_cost']
    
    return costs


def get_monthly_recurring_costs(
    baby_age_months: int,
    cost_level: Literal['low', 'average', 'high']
) -> Dict[str, float]:
    """Get monthly recurring costs by baby age and cost level."""
    costs: Dict[str, float] = {}
    
    for expense in RECURRING_EXPENSES:
        # Check if expense applies to this age
        if baby_age_months >= expense['start_month']:
            if expense['end_month'] is None or baby_age_months <= expense['end_month']:
                cost = 0.0
                if cost_level == 'low':
                    cost = expense['low_cost']
                elif cost_level == 'high':
                    cost = expense['high_cost']
                else:
                    cost = expense['average_cost']
                
                category = expense['category']
                if category not in costs:
                    costs[category] = 0.0
                costs[category] += cost
    
    return costs


def get_baby_expense_assumptions(profile: dict) -> ExpenseAssumptions:
    """
    Get baby expense assumptions based on user profile.
    Ports logic from frontend/src/utils/expenseAssumptions.ts
    """
    # Get childcare preference from profile
    childcare_preference = profile.get('childcare_preference', 'daycare')
    zip_code_found = False
    
    # Try to get childcare costs from Excel file first
    excel_data = get_excel_childcare_cost(profile['zip_code'], childcare_preference)
    
    if excel_data and excel_data.get('infant', 0) > 0:
        # Use data from Excel file
        weekly_infant_cost = excel_data['infant']
        weekly_toddler_cost = excel_data.get('toddler', excel_data['infant'] * 0.88)  # Toddler typically 88% of infant
        zip_code_found = True
    else:
        # Fall back to hardcoded data
        childcare_data = get_childcare_cost_by_zip(profile['zip_code'])
        
        if childcare_data:
            weekly_infant_cost = childcare_data['weekly_infant_cost']
            weekly_toddler_cost = childcare_data['weekly_toddler_cost']
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
    
    # Get one-time costs from reference data
    cost_level_map = {'low': 'low', 'medium': 'average', 'high': 'high'}
    cost_level = cost_level_map[cost_band]
    one_time_costs_data = get_essential_one_time_costs(cost_level)
    
    # Get recurring costs for a newborn (month 0) from reference data
    recurring_costs_month_0 = get_monthly_recurring_costs(0, cost_level)
    
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
            'diapers': recurring_costs_month_0.get('Diapers & Wipes', 105),
            'wipes': 0,  # Included in diapers category
            'formula': recurring_costs_month_0.get('Formula & Food', 150),
            'baby_food': 0,  # Starts at month 6
            'clothing': recurring_costs_month_0.get('Clothing', 50),
            'healthcare': recurring_costs_month_0.get('Healthcare', 75),
            'miscellaneous': recurring_costs_month_0.get('Miscellaneous', 100),
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
        f"Monthly Recurring Costs: Fixed monthly costs include Diapers ($80), Wipes ($15), Food ($150), Supplies ($25), Toys ($20), and Miscellaneous activities/babysitter ($150 in Years 1-2, increasing 20% annually from Year 3 onward). These costs are applied every month throughout the 5-year period.",
        childcare_explanation,
        "Stay-at-Home Parent: If you choose the stay-at-home option, we assume the lower-earning partner will stay home after their parental leave ends. Their income is set to $0 and childcare costs are $0. All other expenses (diapers, food, supplies, etc.) remain the same.",
        "Childcare Cost Reduction: Childcare costs decrease by 20% after year 3 (age 36 months) as children typically require less intensive care and may transition to preschool programs.",
        "Miscellaneous Cost Increase: Miscellaneous expenses (activities, babysitter, etc.) increase by 20% each year starting from Year 3 to account for growing child's expanding needs and activities.",
        "Parental Leave: Income adjustments are calculated based on your specified leave duration and percentage paid.",
        data_source_note,
    ]