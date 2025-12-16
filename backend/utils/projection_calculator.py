"""
Projection calculator module for 5-year baby cost projections.
Ports logic from frontend/src/utils/projectionCalculator.ts
"""

from datetime import datetime
from typing import Dict, List, Literal, TypedDict

from backend.utils.expense_assumptions import (
    ExpenseAssumptions,
    get_baby_expense_assumptions,
)
from backend.data.recurring_loader import get_monthly_recurring_costs as get_recurring_costs_by_year


class IncomeBreakdown(TypedDict):
    partner1: float
    partner2: float
    total: float


class ExpenseBreakdown(TypedDict):
    housing: float
    childcare: float
    diapers: float
    food: float
    healthcare: float
    clothing: float
    one_time: float
    miscellaneous: float
    total: float


class MonthlyProjection(TypedDict):
    month: int
    year: int
    month_of_year: int
    income: IncomeBreakdown
    expenses: ExpenseBreakdown
    net_cashflow: float
    cumulative_savings: float


class YearlyExpenseBreakdown(TypedDict):
    housing: float
    childcare: float
    diapers: float
    food: float
    healthcare: float
    clothing: float
    one_time: float
    miscellaneous: float


class YearlyProjection(TypedDict):
    year: int
    total_income: float
    total_expenses: float
    net_cashflow: float
    ending_savings: float
    expense_breakdown: YearlyExpenseBreakdown


class Warning(TypedDict):
    severity: Literal['critical', 'important', 'informational']
    title: str
    message: str
    months_affected: List[int]
    recommendation: str


class FiveYearProjection(TypedDict):
    profile: dict
    assumptions: ExpenseAssumptions
    monthly_projections: List[MonthlyProjection]
    yearly_projections: List[YearlyProjection]
    total_cost: float
    warnings: List[Warning]
    generated_at: str


def calculate_income_with_leave(
    base_income: float,
    baby_age_months: int,
    leave: dict
) -> float:
    """Calculate income accounting for parental leave."""
    leave_months = leave['duration_weeks'] / 4.33  # Convert weeks to months
    
    if baby_age_months < leave_months:
        # During leave period
        return base_income * (leave['percent_paid'] / 100)
    
    return base_income


def calculate_monthly_expenses(
    baby_age_months: int,
    year: int,
    profile: dict,
    assumptions: ExpenseAssumptions
) -> ExpenseBreakdown:
    """Calculate monthly expenses for a given baby age and year."""
    expenses: ExpenseBreakdown = {
        'housing': profile['monthly_housing_cost'],
        'childcare': 0,
        'diapers': 0,
        'food': 0,
        'healthcare': 0,
        'clothing': 0,
        'one_time': 0,
        'miscellaneous': 0,
        'total': 0,
    }
    
    # One-time costs (all purchased at birth - month 0)
    if baby_age_months == 0:
        expenses['one_time'] += assumptions['one_time_costs']['crib']
        expenses['one_time'] += assumptions['one_time_costs']['stroller']
        expenses['one_time'] += assumptions['one_time_costs']['car_seat']
        expenses['one_time'] += assumptions['one_time_costs']['high_chair']
    
    # Get recurring costs from Excel file (with year-based adjustments)
    recurring_costs = get_recurring_costs_by_year(year)
    
    # Map recurring costs to expense structure
    # All recurring costs are shown under childcare expenses category
    expenses['diapers'] = recurring_costs.get('Diaper', 0)
    expenses['food'] = recurring_costs.get('Food', 0)
    expenses['clothing'] = recurring_costs.get('Supplies', 0)  # Supplies mapped to clothing
    expenses['healthcare'] = recurring_costs.get('Wipes', 0)  # Wipes mapped to healthcare
    expenses['miscellaneous'] = (
        recurring_costs.get('Toys', 0) +
        recurring_costs.get('Miscellaneous ( Activities, Baby sitter etc)', 0)
    )
    
    # Childcare (starts at specified month)
    if baby_age_months >= assumptions['childcare_start_month']:
        base_childcare_cost = 0
        if profile['childcare_preference'] == 'daycare':
            base_childcare_cost = assumptions['childcare_costs']['daycare']
        elif profile['childcare_preference'] == 'nanny':
            base_childcare_cost = assumptions['childcare_costs']['nanny']
        
        # Apply 20% reduction after year 3 (36 months)
        if baby_age_months >= 36:
            expenses['childcare'] = base_childcare_cost * 0.8
        else:
            expenses['childcare'] = base_childcare_cost
        # stay-at-home has no direct cost
    
    expenses['total'] = (
        expenses['housing'] +
        expenses['childcare'] +
        expenses['diapers'] +
        expenses['food'] +
        expenses['healthcare'] +
        expenses['clothing'] +
        expenses['one_time'] +
        expenses['miscellaneous']
    )
    
    return expenses


def aggregate_yearly_projections(
    monthly_projections: List[MonthlyProjection]
) -> List[YearlyProjection]:
    """Aggregate monthly projections into yearly summaries."""
    yearly_data: List[YearlyProjection] = []
    
    for year in range(1, 6):
        year_months = [m for m in monthly_projections if m['year'] == year]
        
        total_income = sum(m['income']['total'] for m in year_months)
        total_expenses = sum(m['expenses']['total'] for m in year_months)
        net_cashflow = total_income - total_expenses
        ending_savings = year_months[-1]['cumulative_savings']
        
        expense_breakdown: YearlyExpenseBreakdown = {
            'housing': sum(m['expenses']['housing'] for m in year_months),
            'childcare': sum(m['expenses']['childcare'] for m in year_months),
            'diapers': sum(m['expenses']['diapers'] for m in year_months),
            'food': sum(m['expenses']['food'] for m in year_months),
            'healthcare': sum(m['expenses']['healthcare'] for m in year_months),
            'clothing': sum(m['expenses']['clothing'] for m in year_months),
            'one_time': sum(m['expenses']['one_time'] for m in year_months),
            'miscellaneous': sum(m['expenses']['miscellaneous'] for m in year_months),
        }
        
        yearly_data.append({
            'year': year,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_cashflow': net_cashflow,
            'ending_savings': ending_savings,
            'expense_breakdown': expense_breakdown,
        })
    
    return yearly_data


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.0f}"


def generate_warnings(
    monthly_projections: List[MonthlyProjection],
    profile: dict,
    assumptions: ExpenseAssumptions
) -> List[Warning]:
    """Generate financial warnings based on projection data."""
    warnings: List[Warning] = []
    
    # Check for negative cashflow months
    negative_cashflow_months = [
        m['month'] for m in monthly_projections if m['net_cashflow'] < 0
    ]
    
    if negative_cashflow_months:
        warnings.append({
            'severity': 'critical',
            'title': 'Negative Cashflow Detected',
            'message': f"Your expenses exceed income in {len(negative_cashflow_months)} month(s) over the 5-year period.",
            'months_affected': negative_cashflow_months,
            'recommendation': 'Consider building an emergency fund before baby arrives, or explore ways to reduce expenses or increase income during these periods.',
        })
    
    # Check for low savings buffer
    min_savings = min(m['cumulative_savings'] for m in monthly_projections)
    recommended_buffer = (profile['partner1_income'] + profile['partner2_income']) * 3  # 3 months expenses
    
    if min_savings < recommended_buffer:
        warnings.append({
            'severity': 'important',
            'title': 'Low Savings Buffer',
            'message': f"Your savings may drop below the recommended 3-month emergency fund ({format_currency(recommended_buffer)}).",
            'months_affected': [],
            'recommendation': 'Try to build up your emergency fund before baby arrives. Aim for at least 3-6 months of expenses.',
        })
    
    # Check for high childcare costs
    childcare_cost = 0.0
    if profile['childcare_preference'] == 'daycare':
        childcare_cost = assumptions['childcare_costs']['daycare']
    elif profile['childcare_preference'] == 'nanny':
        childcare_cost = assumptions['childcare_costs']['nanny']
    
    total_income = profile['partner1_income'] + profile['partner2_income']
    childcare_percentage = (childcare_cost / total_income * 100) if total_income > 0 else 0
    
    if childcare_percentage > 30 and childcare_cost > 0:
        warnings.append({
            'severity': 'important',
            'title': 'High Childcare Costs',
            'message': f"Childcare represents {childcare_percentage:.0f}% of your monthly income ({format_currency(childcare_cost)}/month).",
            'months_affected': [],
            'recommendation': 'Consider exploring alternative childcare options, flexible work arrangements, or whether one partner staying home might be financially comparable.',
        })
    
    # Check parental leave impact
    leave_months = max(
        profile['partner1_leave']['duration_weeks'] / 4.33,
        profile['partner2_leave']['duration_weeks'] / 4.33
    )
    
    if leave_months > 3 and (
        profile['partner1_leave']['percent_paid'] < 100 or
        profile['partner2_leave']['percent_paid'] < 100
    ):
        warnings.append({
            'severity': 'informational',
            'title': 'Extended Parental Leave Period',
            'message': 'Your parental leave extends beyond 3 months with reduced pay.',
            'months_affected': [],
            'recommendation': 'Plan ahead for the income reduction during this period. Consider building extra savings or adjusting discretionary spending.',
        })
    
    return warnings


def calculate_five_year_projection(profile: dict) -> FiveYearProjection:
    """
    Calculate 5-year financial projection for baby expenses.
    Ports logic from frontend/src/utils/projectionCalculator.ts
    """
    assumptions = get_baby_expense_assumptions(profile)
    monthly_projections: List[MonthlyProjection] = []
    
    cumulative_savings = profile['current_savings']
    
    # Determine if stay-at-home parent and which partner stays home
    is_stay_at_home = profile.get('childcare_preference') == 'stay-at-home'
    lower_earner_is_partner1 = profile['partner1_income'] <= profile['partner2_income']
    
    # Calculate 60 months (5 years)
    for month in range(1, 61):
        year = (month - 1) // 12 + 1
        month_of_year = ((month - 1) % 12) + 1
        baby_age_months = month - 1  # Month 1 = baby is 0 months old
        
        # Calculate income (accounting for parental leave and stay-at-home)
        partner1_income = calculate_income_with_leave(
            profile['partner1_income'],
            baby_age_months,
            profile['partner1_leave']
        )
        partner2_income = calculate_income_with_leave(
            profile['partner2_income'],
            baby_age_months,
            profile['partner2_leave']
        )
        
        # If stay-at-home, set lower earner's income to zero after parental leave
        if is_stay_at_home:
            # Determine when parental leave ends for the stay-at-home parent
            if lower_earner_is_partner1:
                leave_end_month = profile['partner1_leave']['duration_weeks'] / 4.33
                if baby_age_months >= leave_end_month:
                    partner1_income = 0
            else:
                leave_end_month = profile['partner2_leave']['duration_weeks'] / 4.33
                if baby_age_months >= leave_end_month:
                    partner2_income = 0
        
        total_income = partner1_income + partner2_income
        
        # Calculate expenses using recurring costs from Excel
        expenses = calculate_monthly_expenses(
            baby_age_months,
            year,
            profile,
            assumptions
        )
        
        net_cashflow = total_income - expenses['total']
        cumulative_savings += net_cashflow
        
        monthly_projections.append({
            'month': month,
            'year': year,
            'month_of_year': month_of_year,
            'income': {
                'partner1': partner1_income,
                'partner2': partner2_income,
                'total': total_income,
            },
            'expenses': expenses,
            'net_cashflow': net_cashflow,
            'cumulative_savings': cumulative_savings,
        })
    
    # Aggregate into yearly projections
    yearly_projections = aggregate_yearly_projections(monthly_projections)
    
    # Calculate total cost
    total_cost = sum(year['total_expenses'] for year in yearly_projections)
    
    # Generate warnings
    warnings = generate_warnings(monthly_projections, profile, assumptions)
    
    return {
        'profile': profile,
        'assumptions': assumptions,
        'monthly_projections': monthly_projections,
        'yearly_projections': yearly_projections,
        'total_cost': total_cost,
        'warnings': warnings,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
    }