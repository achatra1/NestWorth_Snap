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
    total_healthcare = sum(y["expenseBreakdown"]["healthcare"] for y in yearly)
    total_clothing = sum(y["expenseBreakdown"]["clothing"] for y in yearly)
    one_time_costs = sum(y["expenseBreakdown"]["oneTime"] for y in yearly)
    total_misc = sum(y["expenseBreakdown"]["miscellaneous"] for y in yearly)
    
    # Calculate baby-specific costs (excluding housing)
    total_baby_costs = total_childcare + total_diapers + total_food + total_healthcare + total_clothing + one_time_costs + total_misc
    
    # Calculate parental leave income loss
    partner1_leave_weeks = profile["partner1Leave"]["durationWeeks"]
    partner1_leave_percent = profile["partner1Leave"]["percentPaid"]
    partner2_leave_weeks = profile["partner2Leave"]["durationWeeks"]
    partner2_leave_percent = profile["partner2Leave"]["percentPaid"]
    
    partner1_income_loss = (profile["partner1Income"] * 52 / 12) * partner1_leave_weeks * (1 - partner1_leave_percent / 100)
    partner2_income_loss = (profile["partner2Income"] * 52 / 12) * partner2_leave_weeks * (1 - partner2_leave_percent / 100)
    total_leave_income_loss = partner1_income_loss + partner2_income_loss
    
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
- Total Healthcare (5 years): ${total_healthcare:,.0f}
- Total Clothing (5 years): ${total_clothing:,.0f}
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
  - Healthcare: ${year["expenseBreakdown"]["healthcare"]:,.0f}
  - Clothing: ${year["expenseBreakdown"]["clothing"]:,.0f}
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

Create a comprehensive, empathetic markdown summary with these sections:

1. **Executive Summary** - Brief overview with key totals
2. **Life Stage Breakdown** - Year 0-1 (Infant), Year 1-3 (Toddler), Year 3-5 (Preschool)
3. **Childcare Analysis** - Detailed look at childcare costs and impact
4. **Cost Structure** - One-time vs recurring breakdown
5. **Financial Pressure Points** - Identify challenging periods
6. **Planning Insights** - 3-5 actionable recommendations

**Tone Guidelines:**
- Empathetic and supportive (this is a major life transition)
- Clear and structured (use markdown formatting)
- Realistic but encouraging
- Focus on planning and preparation, not fear

**Format Requirements:**
- Use markdown headers (##, ###)
- Include tables where appropriate
- Use bullet points for lists
- Format all currency as $X,XXX (no decimals)
- Keep paragraphs concise

**REMEMBER**: Use ONLY the numbers provided above. Do not calculate or estimate any new values.
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
            "content": """You are a professional, fiduciary-minded financial advisor.
Your goal is to help me understand my budget clearly, surface risks and tradeoffs, and give practical, conservative financial advice.

Your tone should be calm, neutral, and grounded — not salesy, not alarmist, and not overly optimistic.
You should assume I want long-term financial stability over short-term optimization.

You provide clear, structured advice using only the data provided to you."""
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