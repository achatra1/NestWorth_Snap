"""AI-powered assumptions summarization using OpenAI API."""
from typing import Any
from backend.integrations.openai_client import generate_chat_completion


def build_assumptions_prompt(assumptions: dict[str, Any]) -> str:
    """
    Build a structured prompt for AI assumptions summarization.
    
    Args:
        assumptions: Assumptions object from projection
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""You are an expert financial analyst and communicator.
Your task is to summarize the assumptions used in this analysis so that a non-expert user can quickly understand what the results depend on.

## Assumptions Data:

**Cost Band:** {assumptions.get('costBand', 'N/A')}

**One-Time Costs:**
- Crib: ${assumptions.get('oneTimeCosts', {}).get('crib', 0):,.0f}
- Stroller: ${assumptions.get('oneTimeCosts', {}).get('stroller', 0):,.0f}
- Car Seat: ${assumptions.get('oneTimeCosts', {}).get('carSeat', 0):,.0f}
- High Chair: ${assumptions.get('oneTimeCosts', {}).get('highChair', 0):,.0f}

**Monthly Recurring Costs:**
- Diapers: ${assumptions.get('monthlyRecurring', {}).get('diapers', 0):,.0f}
- Wipes: ${assumptions.get('monthlyRecurring', {}).get('wipes', 0):,.0f}
- Formula: ${assumptions.get('monthlyRecurring', {}).get('formula', 0):,.0f}
- Clothing: ${assumptions.get('monthlyRecurring', {}).get('clothing', 0):,.0f}
- Healthcare: ${assumptions.get('monthlyRecurring', {}).get('healthcare', 0):,.0f}
- Miscellaneous: ${assumptions.get('monthlyRecurring', {}).get('miscellaneous', 0):,.0f}

**Childcare Costs:**
- Daycare: ${assumptions.get('childcareCosts', {}).get('daycare', 0):,.0f}/month
- Nanny: ${assumptions.get('childcareCosts', {}).get('nanny', 0):,.0f}/month
- Stay-at-Home: ${assumptions.get('childcareCosts', {}).get('stayAtHome', 0):,.0f}/month
- Childcare Start Month: {assumptions.get('childcareStartMonth', 'N/A')}
- ZIP Code Found: {assumptions.get('zipCodeFound', False)}

## Instructions:

Keep the summary short, scannable, and precise
Preserve important details, but remove low-signal explanations
Translate technical or numeric assumptions into plain-English implications
Emphasize assumptions that would materially change outcomes if wrong
Avoid hedging language unless uncertainty is meaningful

## What to Include:

**Core Assumptions (Must-Hold)**
- Assumptions that drive most of the outcome
- Phrase as clear statements (not paragraphs)

**Financial Sensitivity Triggers**
- Inputs where small changes → large impact
- Call these out explicitly (e.g., "Most sensitive to…")

**Timing & Duration Assumptions**
- Anything related to start dates, duration, or phase-changes

**What This Does Not Assume**
- Explicitly state what is excluded to prevent misinterpretation

## Formatting Rules:

- Use bullet points only
- Limit to 6–10 bullets total
- Each bullet should be one sentence max
- Use **bold text** to highlight the variable or concept being assumed
- Avoid repeating numbers unless they are essential

Generate the assumptions summary now:"""
    
    return prompt


async def generate_assumptions_summary(assumptions: dict[str, Any]) -> str:
    """
    Generate AI summary of assumptions.
    
    Args:
        assumptions: Assumptions object from projection
    
    Returns:
        Markdown-formatted assumptions summary
    
    Raises:
        Exception: If OpenAI API call fails
    """
    prompt = build_assumptions_prompt(assumptions)
    
    messages = [
        {
            "role": "system",
            "content": "You are an expert financial analyst and communicator specializing in making complex financial assumptions clear and actionable for non-expert users."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    summary = await generate_chat_completion(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.5,  # Lower temperature for more consistent, factual output
        max_tokens=800
    )
    
    return summary