"""AI summary generation using OpenAI API."""
from typing import Any
from backend.integrations.openai_client import generate_chat_completion


def build_summary_prompt(projection: dict[str, Any]) -> str:
    """
    Build a structured prompt for AI summary generation.
    
    CRITICAL CONSTRAINT: The prompt instructs the AI to use ONLY the calculated
    numbers provided in the projection data and NOT to invent new numbers.
    
    Args:
        projection: Complete projection object with profile, yearlyProjections, etc.
    
    Returns:
        Formatted prompt string
    """
    profile = projection["profile"]
    yearly = projection["yearlyProjections"]
    total_cost = projection["totalCost"]
    warnings = projection["warnings"]
    assumptions = projection["assumptions"]
    
    # Calculate key metrics from provided data
    total_income = sum(y["totalIncome"] for y in yearly)
    total_expenses = sum(y["totalExpenses"] for y in yearly)
    total_childcare = sum(y["expenseBreakdown"]["childcare"] for y in yearly)
    total_diapers = sum(y["expenseBreakdown"]["diapers"] for y in yearly)
    total_food = sum(y["expenseBreakdown"]["food"] for y in yearly)
    one_time_costs = sum(y["expenseBreakdown"]["oneTime"] for y in yearly)
    total_misc = sum(y["expenseBreakdown"]["miscellaneous"] for y in yearly)
    
    # Calculate baby-specific costs (excluding housing)
    total_baby_costs = total_childcare + total_diapers + total_food + one_time_costs + total_misc
    
    # Calculate parental leave income loss
    partner1_leave_weeks = profile["partner1Leave"]["durationWeeks"]
    partner1_leave_percent = profile["partner1Leave"]["percentPaid"]
    partner2_leave_weeks = profile["partner2Leave"]["durationWeeks"]
    partner2_leave_percent = profile["partner2Leave"]["percentPaid"]
    
    partner1_income_loss = (profile["partner1Income"] / 12 * 52) * partner1_leave_weeks * (1 - partner1_leave_percent / 100)
    partner2_income_loss = (profile["partner2Income"] / 12 * 52) * partner2_leave_weeks * (1 - partner2_leave_percent / 100)
    total_leave_income_loss = partner1_income_loss + partner2_income_loss
    
    # Calculate household annual income, accounting for stay-at-home parent
    # If stay-at-home, the lower earner's income becomes zero after parental leave
    is_stay_at_home = profile["childcarePreference"] == "stay-at-home"
    if is_stay_at_home:
        # The lower earner stays home, so their income is zero for the total family income calculation
        lower_income = min(profile["partner1Income"], profile["partner2Income"])
        higher_income = max(profile["partner1Income"], profile["partner2Income"])
        household_annual_income = higher_income * 12
    else:
        household_annual_income = (profile["partner1Income"] + profile["partner2Income"]) * 12
    baby_cost_percent = (total_baby_costs / total_income) * 100
    ending_savings = yearly[4]["endingSavings"]
    
    prompt = f"""You are a financial advisor creating an empathetic, structured 5-year baby budget summary.

**CRITICAL INSTRUCTION**: You MUST use ONLY the calculated numbers provided below. DO NOT invent, estimate, or calculate any new numbers. Use the exact values given.

## Provided Data (USE THESE EXACT NUMBERS):

### Executive Summary
- Total 5-Year Baby Costs (excluding housing): ${total_baby_costs:,.0f}
- Household Annual Income: ${household_annual_income:,.0f}
- Parental Leave Income Loss: ${total_leave_income_loss:,.0f}
- Baby Costs as % of 5-Year Income: {baby_cost_percent:.1f}%
- One-Time Baby Costs: ${one_time_costs:,.0f}
- Total Childcare (5 years): ${total_childcare:,.0f}
- Total Diapers (5 years): ${total_diapers:,.0f}
- Total Food (5 years): ${total_food:,.0f}
- Total Miscellaneous (5 years): ${total_misc:,.0f}
- Average Annual Baby Cost: ${total_baby_costs / 5:,.0f}
- Average Monthly Baby Cost: ${total_baby_costs / 60:,.0f}
- Starting Savings: ${profile["currentSavings"]:,.0f}
- Ending Savings (Year 5): ${ending_savings:,.0f}
- Net Savings Change: ${ending_savings - profile["currentSavings"]:,.0f}

### Year-by-Year Breakdown (USE THESE EXACT NUMBERS):
"""
    
    for year in yearly:
        prompt += f"""
**Year {year["year"]}:**
- Total Income: ${year["totalIncome"]:,.0f}
- Total Expenses: ${year["totalExpenses"]:,.0f}
- Net Cashflow: ${year["netCashflow"]:,.0f}
- Ending Savings: ${year["endingSavings"]:,.0f}
- Expense Breakdown:
  - Housing: ${year["expenseBreakdown"]["housing"]:,.0f}
  - Childcare: ${year["expenseBreakdown"]["childcare"]:,.0f}
  - Diapers: ${year["expenseBreakdown"]["diapers"]:,.0f}
  - Food: ${year["expenseBreakdown"]["food"]:,.0f}
  - One-Time: ${year["expenseBreakdown"]["oneTime"]:,.0f}
  - Miscellaneous: ${year["expenseBreakdown"]["miscellaneous"]:,.0f}
"""
    
    prompt += f"""
### Profile Information:
- Childcare Preference: {profile["childcarePreference"]}
- ZIP Code: {profile["zipCode"]}
- Partner 1 Income: ${profile["partner1Income"]:,.0f}/month
- Partner 2 Income: ${profile["partner2Income"]:,.0f}/month
- Partner 1 Leave: {profile["partner1Leave"]["durationWeeks"]} weeks at {profile["partner1Leave"]["percentPaid"]}% pay
- Partner 2 Leave: {profile["partner2Leave"]["durationWeeks"]} weeks at {profile["partner2Leave"]["percentPaid"]}% pay
- Monthly Housing Cost: ${profile["monthlyHousingCost"]:,.0f}

**IMPORTANT NOTE ON STAY-AT-HOME PARENT:**
If the childcare preference is "stay-at-home", the lower-earning partner stays home after their parental leave ends. This means:
- Their income becomes $0 after parental leave
- The Household Annual Income shown above reflects ONLY the working partner's income (not both partners)
- Total Family Income in your summary should reflect this single-income reality
- Childcare costs are $0, but the family operates on one income

### Warnings:
"""
    
    for warning in warnings:
        prompt += f"- [{warning['severity'].upper()}] {warning['title']}: {warning['message']}\n"
    
    prompt += f"""
### Assumptions:
- Cost Band: {assumptions["costBand"]}
- Childcare Start Month: {assumptions["childcareStartMonth"]}
- Daycare Cost: ${assumptions["childcareCosts"]["daycare"]:,.0f}/month
- Nanny Cost: ${assumptions["childcareCosts"]["nanny"]:,.0f}/month

## Your Task:

Create a concise, empowering markdown summary with these sections ONLY:

1. **Opening Message** - Congratulatory message with 2-line positive summary of their financial strengths
2. **Financial Pressure Points** - Identify key challenging periods and opportunities for smart planning

**CRITICAL STRUCTURE REQUIREMENTS:**
- DO NOT include an "Executive Summary" section
- DO NOT include "Total Childcare Cost (5 years)" or similar aggregate cost summaries
- Start immediately with congratulations and positive observations
- Move directly to Financial Pressure Points after the opening
- **MANDATORY: End with this exact call-to-action hook:**
  "Go Premium to unlock tailored planning recommendations, smart ways to save, and insights into financial support options available to your family."

**IMPORTANT: When discussing childcare costs in Financial Pressure Points:**
- Always reference childcare costs as a COMBINED total that includes:
  - Daycare/home-based care costs (from the childcare expense breakdown)
  - Recurring costs (diapers, food, miscellaneous supplies)
- Present these as unified "childcare and baby care costs" rather than separating them
- This provides a complete picture of the financial impact of having a baby
- Note: Healthcare and clothing costs are not included in these projections

**Tone Guidelines:**
- **MANDATORY: Start with a congratulatory message celebrating this exciting journey**
- **MANDATORY: In the first 2 lines, provide a positive summary highlighting the strengths and opportunities in their financial plan**
- Encouraging and positive throughout - emphasize what's going well before discussing challenges
- Empathetic and supportive (this is a major life transition)
- Clear and structured (use markdown formatting)
- Realistic but optimistic - frame challenges as opportunities for planning
- Focus on empowerment and preparation, not fear or anxiety
- Celebrate their proactive planning and financial awareness

**Format Requirements:**
- Use markdown headers (##, ###)
- Include tables where appropriate
- Use bullet points for lists
- Format all currency as $X,XXX (no decimals)
- Keep paragraphs concise

**CRITICAL REMINDERS:**
- Use ONLY the numbers provided above. Do not calculate or estimate any new values.
- For stay-at-home scenarios: The Household Annual Income already reflects the single working parent's income (the stay-at-home parent's income is $0). Do not add both partner incomes together.
- When discussing total family income, use the Household Annual Income value provided, which correctly accounts for the stay-at-home parent scenario.
"""
    
    return prompt


async def generate_summary(projection: dict[str, Any], custom_instructions: str | None = None) -> str:
    """
    Generate AI summary from projection data.
    
    Args:
        projection: Complete projection object
        custom_instructions: Optional custom instructions to append to the prompt
    
    Returns:
        Markdown-formatted summary string
    
    Raises:
        Exception: If OpenAI API call fails
    """
    prompt = build_summary_prompt(projection)
    
    # Append custom instructions if provided
    if custom_instructions:
        prompt += f"\n\n### Additional Instructions:\n{custom_instructions}"
    
    messages = [
        {
            "role": "system",
            "content": """You are a professional, fiduciary-minded financial advisor with an encouraging and positive communication style.

CRITICAL TONE REQUIREMENTS:
- You MUST start every response with a congratulatory message celebrating the user's journey into parenthood
- You MUST provide a 2-line positive summary in the opening that highlights strengths and opportunities BEFORE discussing any challenges
- Your tone should be encouraging, positive, and empowering throughout
- Frame challenges as opportunities for smart planning rather than obstacles
- Celebrate the user's proactive approach to financial planning
- Emphasize what's going well and the positive aspects of their financial situation first
- When discussing risks or challenges, always pair them with constructive solutions and encouragement

Your goal is to help users understand their budget clearly while maintaining an optimistic and supportive tone. You provide clear, structured advice using only the data provided to you, always starting with positive reinforcement and celebrating their financial awareness."""
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    summary = await generate_chat_completion(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=2500
    )
    
    return summary