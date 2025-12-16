"""PDF generation utility for NestWorth projections."""
from io import BytesIO
from datetime import datetime
from typing import Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
import re


def parse_markdown_to_paragraphs(markdown_text: str, styles) -> list:
    """
    Simple markdown parser that converts markdown to reportlab Paragraphs.
    Handles: headers (# ## ###), bold (**text**), lists (- item), and paragraphs.
    """
    elements = []
    lines = markdown_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Headers
        if line.startswith('### '):
            text = line[4:].strip()
            elements.append(Paragraph(text, styles['Heading3']))
            elements.append(Spacer(1, 0.1 * inch))
        elif line.startswith('## '):
            text = line[3:].strip()
            elements.append(Paragraph(text, styles['Heading2']))
            elements.append(Spacer(1, 0.15 * inch))
        elif line.startswith('# '):
            text = line[2:].strip()
            elements.append(Paragraph(text, styles['Heading1']))
            elements.append(Spacer(1, 0.2 * inch))
        # List items
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Convert markdown bold to HTML bold
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(f"• {text}", styles['BodyText']))
            elements.append(Spacer(1, 0.05 * inch))
        # Regular paragraphs
        else:
            # Convert markdown bold to HTML bold
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            elements.append(Paragraph(text, styles['BodyText']))
            elements.append(Spacer(1, 0.1 * inch))
        
        i += 1
    
    return elements


def format_currency(amount: float) -> str:
    """Format a number as currency."""
    return f"${amount:,.2f}"


def generate_pdf(projection: dict[str, Any], summary: str) -> BytesIO:
    """
    Generate a PDF document from projection and AI summary.
    
    Args:
        projection: Complete projection object with profile, yearlyProjections, warnings, etc.
        summary: Markdown-formatted AI summary
    
    Returns:
        BytesIO: PDF file as binary stream
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Extract profile and projections early for use throughout
    profile = projection.get('profile', {})
    yearly_projections = projection.get('yearlyProjections', [])
    monthly_projections = projection.get('monthlyProjections', [])
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=20,
        alignment=TA_LEFT
    )
    
    # Title
    elements.append(Paragraph("Your Baby Blueprint", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    elements.append(Spacer(1, 0.5 * inch))
    
    # ============================================================
    # SECTION 1: FINANCIAL BLUEPRINT (AI Summary)
    # ============================================================
    elements.append(Paragraph("Financial Blueprint", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Parse markdown summary
    summary_elements = parse_markdown_to_paragraphs(summary, styles)
    elements.extend(summary_elements)
    
    # Page break before monthly breakdown
    elements.append(PageBreak())
    
    # ============================================================
    # SECTION 2: DETAILED YEAR-BY-YEAR BREAKDOWN
    # ============================================================
    elements.append(Paragraph("Year-by-Year Financial Breakdown", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    childcare_pref = profile.get('childcarePreference', 'N/A').replace('-', ' ').title()
    
    # Create detailed breakdown for each year
    for year_proj in yearly_projections:
        year_num = year_proj.get('year', 0)
        expense_breakdown = year_proj.get('expenseBreakdown', {})
        
        # Year header
        year_header_style = ParagraphStyle(
            'YearHeader',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=8,
            spaceBefore=12
        )
        elements.append(Paragraph(f"Year {year_num}", year_header_style))
        
        # Calculate income breakdown for this year
        year_months = [m for m in monthly_projections if m.get('year') == year_num]
        partner1_income = sum(m.get('income', {}).get('partner1', 0) for m in year_months)
        partner2_income = sum(m.get('income', {}).get('partner2', 0) for m in year_months)
        total_income = partner1_income + partner2_income
        
        # Calculate expense categories
        housing = expense_breakdown.get('housing', 0)
        credit_card = expense_breakdown.get('creditCard', 0)
        childcare = expense_breakdown.get('childcare', 0)
        diapers = expense_breakdown.get('diapers', 0)
        food = expense_breakdown.get('food', 0)
        one_time = expense_breakdown.get('oneTime', 0)
        miscellaneous = expense_breakdown.get('miscellaneous', 0)
        
        household_expenses = housing + credit_card
        childcare_expenses = childcare + diapers + food + one_time + miscellaneous
        total_expenses = year_proj.get('totalExpenses', 0)
        net_cashflow = year_proj.get('netCashflow', 0)
        ending_savings = year_proj.get('endingSavings', 0)
        
        # Build detailed breakdown table
        breakdown_data = []
        
        # Income section
        breakdown_data.append(['INCOME BREAKDOWN', ''])
        breakdown_data.append(['  Partner 1 Income', format_currency(partner1_income)])
        breakdown_data.append(['  Partner 2 Income', format_currency(partner2_income)])
        breakdown_data.append(['Total Income', format_currency(total_income)])
        breakdown_data.append(['', ''])
        
        # Household expenses section
        breakdown_data.append(['HOUSEHOLD EXPENSES', ''])
        breakdown_data.append(['  Housing (Rent/Mortgage)', format_currency(housing)])
        breakdown_data.append([f'    ({format_currency(housing / 12)}/month × 12 months)', ''])
        if credit_card > 0:
            breakdown_data.append(['  Credit Card Payments', format_currency(credit_card)])
            breakdown_data.append([f'    ({format_currency(credit_card / 12)}/month × 12 months)', ''])
        breakdown_data.append(['Household Subtotal', format_currency(household_expenses)])
        breakdown_data.append(['', ''])
        
        # Childcare expenses section
        breakdown_data.append(['CHILDCARE EXPENSES', ''])
        if childcare > 0:
            breakdown_data.append([f'  Childcare ({childcare_pref})', format_currency(childcare)])
            if year_num == 1:
                breakdown_data.append([f'    ({format_currency(childcare / 6)}/month × 6 months, starts month 6)', ''])
            else:
                breakdown_data.append([f'    ({format_currency(childcare / 12)}/month × 12 months)', ''])
        if diapers > 0:
            breakdown_data.append(['  Diapers & Wipes', format_currency(diapers)])
            breakdown_data.append([f'    ({format_currency(diapers / 12)}/month × 12 months)', ''])
        if food > 0:
            breakdown_data.append(['  Food (Formula/Baby Food)', format_currency(food)])
            breakdown_data.append([f'    ({format_currency(food / 12)}/month × 12 months)', ''])
        if one_time > 0:
            breakdown_data.append(['  One-Time Items (Crib, Stroller, etc.)', format_currency(one_time)])
        if miscellaneous > 0:
            breakdown_data.append(['  Miscellaneous (Toys, Books, etc.)', format_currency(miscellaneous)])
            breakdown_data.append([f'    ({format_currency(miscellaneous / 12)}/month × 12 months)', ''])
        breakdown_data.append(['Childcare Subtotal', format_currency(childcare_expenses)])
        breakdown_data.append(['', ''])
        
        # Totals section
        breakdown_data.append(['TOTAL EXPENSES', format_currency(total_expenses)])
        breakdown_data.append(['  Monthly Average', format_currency(total_expenses / 12)])
        breakdown_data.append(['', ''])
        breakdown_data.append(['NET CASHFLOW', format_currency(net_cashflow)])
        breakdown_data.append(['  Monthly Average', format_currency(net_cashflow / 12)])
        breakdown_data.append(['  Savings Rate', f"{((net_cashflow / total_income) * 100):.1f}%"])
        breakdown_data.append(['', ''])
        breakdown_data.append(['ENDING SAVINGS', format_currency(ending_savings)])
        
        # Create table with safe, minimal styling
        table_style = [
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]
        
        # Find and style section headers dynamically
        for i, row in enumerate(breakdown_data):
            row_text = row[0].strip()
            # Bold formatting for headers and totals
            if row_text in ['INCOME BREAKDOWN', 'Total Income', 'HOUSEHOLD EXPENSES',
                           'Household Subtotal', 'CHILDCARE EXPENSES', 'Childcare Subtotal',
                           'TOTAL EXPENSES', 'NET CASHFLOW', 'ENDING SAVINGS']:
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                
            # Background colors for major sections
            if row_text == 'INCOME BREAKDOWN':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#e5e7eb')))
            elif row_text == 'Total Income':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f3f4f6')))
                table_style.append(('LINEABOVE', (0, i), (-1, i), 1, colors.grey))
            elif row_text in ['HOUSEHOLD EXPENSES', 'CHILDCARE EXPENSES']:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#e5e7eb')))
            elif row_text == 'TOTAL EXPENSES':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#dbeafe')))
                table_style.append(('LINEABOVE', (0, i), (-1, i), 1.5, colors.grey))
            elif row_text == 'NET CASHFLOW':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#dcfce7')))
                table_style.append(('LINEABOVE', (0, i), (-1, i), 1, colors.grey))
            elif row_text == 'ENDING SAVINGS':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#e0e7ff')))
                table_style.append(('LINEABOVE', (0, i), (-1, i), 1, colors.grey))
        
        breakdown_table = Table(breakdown_data, colWidths=[4.5 * inch, 2 * inch])
        breakdown_table.setStyle(TableStyle(table_style))
        
        elements.append(breakdown_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Add page break after each year except the last
        if year_num < len(yearly_projections):
            elements.append(PageBreak())
    
    # Page break before assumptions
    elements.append(PageBreak())
    
    # ============================================================
    # SECTION 3: ASSUMPTIONS
    # ============================================================
    elements.append(Paragraph("Calculation Assumptions", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    assumptions = projection.get('assumptions', {})
    
    # Build comprehensive assumptions list
    assumptions_data = []
    header_rows = []  # Track which rows are section headers
    
    # Income assumptions
    header_rows.append(len(assumptions_data))
    assumptions_data.append(['Income', ''])
    assumptions_data.append(['  Partner 1 Monthly Income', format_currency(profile.get('partner1Income', 0))])
    assumptions_data.append(['  Partner 2 Monthly Income', format_currency(profile.get('partner2Income', 0))])
    assumptions_data.append(['  Current Savings', format_currency(profile.get('currentSavings', 0))])
    assumptions_data.append(['', ''])
    
    # One-time costs
    one_time = assumptions.get('oneTimeCosts', {})
    if one_time:
        header_rows.append(len(assumptions_data))
        assumptions_data.append(['One-Time Costs', ''])
        for key, value in one_time.items():
            label = key.replace('_', ' ').title()
            assumptions_data.append([f"  {label}", format_currency(value)])
        assumptions_data.append(['', ''])
    
    # Recurring costs
    recurring = assumptions.get('recurringCosts', {})
    if recurring:
        header_rows.append(len(assumptions_data))
        assumptions_data.append(['Monthly Recurring Costs', ''])
        for key, value in recurring.items():
            label = key.replace('_', ' ').title()
            assumptions_data.append([f"  {label}", format_currency(value)])
        assumptions_data.append(['', ''])
    
    # Childcare costs
    childcare = assumptions.get('childcareCosts', {})
    if childcare:
        header_rows.append(len(assumptions_data))
        assumptions_data.append(['Childcare', ''])
        assumptions_data.append([f"  Preference", profile.get('childcarePreference', 'N/A').replace('-', ' ').title()])
        assumptions_data.append([f"  Monthly Cost", format_currency(childcare.get('monthlyCost', 0))])
        assumptions_data.append([f"  Start Month", str(childcare.get('startMonth', 0))])
        assumptions_data.append(['', ''])
    
    # Other profile details
    header_rows.append(len(assumptions_data))
    assumptions_data.append(['Other Details', ''])
    assumptions_data.append([f"  ZIP Code", profile.get('zipCode', 'N/A')])
    assumptions_data.append([f"  Due Date", profile.get('dueDate', 'N/A')])
    
    if assumptions_data:
        # Build table style dynamically
        table_style = [
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Add bold formatting for section headers dynamically
        for row_idx in header_rows:
            if row_idx < len(assumptions_data):
                table_style.append(('FONTNAME', (0, row_idx), (0, row_idx), 'Helvetica-Bold'))
        
        assumptions_table = Table(assumptions_data, colWidths=[4.5 * inch, 2 * inch])
        assumptions_table.setStyle(TableStyle(table_style))
        
        elements.append(assumptions_table)
    
    # Page break before upgrade call
    elements.append(PageBreak())
    
    # ============================================================
    # UPGRADE TO PREMIUM CALL
    # ============================================================
    upgrade_title_style = ParagraphStyle(
        'UpgradeTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    upgrade_text_style = ParagraphStyle(
        'UpgradeText',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12,
        alignment=TA_CENTER,
        leading=18
    )
    
    elements.append(Spacer(1, 1.5 * inch))
    elements.append(Paragraph("Unlock Your Full Financial Potential", upgrade_title_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    elements.append(Paragraph(
        "Upgrade to <b>NestWorth Premium</b> for:",
        upgrade_text_style
    ))
    elements.append(Spacer(1, 0.2 * inch))
    
    premium_features = [
        "✓ Detailed month-by-month expense tracking",
        "✓ Customizable financial scenarios and what-if analysis",
        "✓ Advanced savings optimization strategies",
        "✓ Real-time updates as your situation changes",
        "✓ Export to Excel for deeper analysis",
        "✓ Priority support from financial planning experts"
    ]
    
    feature_style = ParagraphStyle(
        'FeatureText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        leftIndent=100,
        alignment=TA_LEFT
    )
    
    for feature in premium_features:
        elements.append(Paragraph(feature, feature_style))
    
    elements.append(Spacer(1, 0.4 * inch))
    
    cta_style = ParagraphStyle(
        'CTAText',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph(
        "Visit nestworth.com/premium to upgrade today!",
        cta_style
    ))
    
    # Build PDF
    doc.build(elements)
    
    # Reset buffer position to beginning
    buffer.seek(0)
    
    return buffer