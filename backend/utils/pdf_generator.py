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
    # SECTION 2: MONTHLY INCOME & EXPENSES (Years 1-5)
    # ============================================================
    elements.append(Paragraph("Monthly Income & Expenses Breakdown", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    yearly_projections = projection.get('yearlyProjections', [])
    
    # Create Excel-style grid for each year
    for year_proj in yearly_projections:
        year_num = year_proj.get('year', 0)
        monthly_projections = year_proj.get('monthlyProjections', [])
        
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
        
        # Build monthly table
        monthly_data = [['Month', 'Income', 'Expenses', 'Net Cashflow', 'Balance']]
        
        for month_proj in monthly_projections:
            month_num = month_proj.get('month', 0)
            income = month_proj.get('income', 0)
            expenses = month_proj.get('expenses', 0)
            net_cashflow = month_proj.get('netCashflow', 0)
            ending_balance = month_proj.get('endingBalance', 0)
            
            monthly_data.append([
                f"Month {month_num}",
                format_currency(income),
                format_currency(expenses),
                format_currency(net_cashflow),
                format_currency(ending_balance)
            ])
        
        # Add year totals row
        year_total_income = year_proj.get('totalIncome', 0)
        year_total_expenses = year_proj.get('totalExpenses', 0)
        year_net_cashflow = year_proj.get('netCashflow', 0)
        year_ending_balance = year_proj.get('endingBalance', 0)
        
        monthly_data.append([
            'Year Total',
            format_currency(year_total_income),
            format_currency(year_total_expenses),
            format_currency(year_net_cashflow),
            format_currency(year_ending_balance)
        ])
        
        # Create table with Excel-style formatting
        monthly_table = Table(monthly_data, colWidths=[1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
        monthly_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 5),
            ('TOPPADDING', (0, 1), (-1, -2), 5),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ('TOPPADDING', (0, -1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(monthly_table)
        elements.append(Spacer(1, 0.2 * inch))
    
    # Page break before assumptions
    elements.append(PageBreak())
    
    # ============================================================
    # SECTION 3: ASSUMPTIONS
    # ============================================================
    elements.append(Paragraph("Calculation Assumptions", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    assumptions = projection.get('assumptions', {})
    profile = projection.get('profile', {})
    
    # Build comprehensive assumptions list
    assumptions_data = []
    
    # Income assumptions
    assumptions_data.append(['Income', ''])
    assumptions_data.append(['  Partner 1 Monthly Income', format_currency(profile.get('partner1Income', 0))])
    assumptions_data.append(['  Partner 2 Monthly Income', format_currency(profile.get('partner2Income', 0))])
    assumptions_data.append(['  Current Savings', format_currency(profile.get('currentSavings', 0))])
    assumptions_data.append(['', ''])
    
    # One-time costs
    one_time = assumptions.get('oneTimeCosts', {})
    if one_time:
        assumptions_data.append(['One-Time Costs', ''])
        for key, value in one_time.items():
            label = key.replace('_', ' ').title()
            assumptions_data.append([f"  {label}", format_currency(value)])
        assumptions_data.append(['', ''])
    
    # Recurring costs
    recurring = assumptions.get('recurringCosts', {})
    if recurring:
        assumptions_data.append(['Monthly Recurring Costs', ''])
        for key, value in recurring.items():
            label = key.replace('_', ' ').title()
            assumptions_data.append([f"  {label}", format_currency(value)])
        assumptions_data.append(['', ''])
    
    # Childcare costs
    childcare = assumptions.get('childcareCosts', {})
    if childcare:
        assumptions_data.append(['Childcare', ''])
        assumptions_data.append([f"  Preference", profile.get('childcarePreference', 'N/A').replace('-', ' ').title()])
        assumptions_data.append([f"  Monthly Cost", format_currency(childcare.get('monthlyCost', 0))])
        assumptions_data.append([f"  Start Month", str(childcare.get('startMonth', 0))])
        assumptions_data.append(['', ''])
    
    # Other profile details
    assumptions_data.append(['Other Details', ''])
    assumptions_data.append([f"  ZIP Code", profile.get('zipCode', 'N/A')])
    assumptions_data.append([f"  Due Date", profile.get('dueDate', 'N/A')])
    
    if assumptions_data:
        assumptions_table = Table(assumptions_data, colWidths=[4.5 * inch, 2 * inch])
        assumptions_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            # Bold category headers
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
            ('FONTNAME', (0, 10), (0, 10), 'Helvetica-Bold'),
            ('FONTNAME', (0, 14), (0, 14), 'Helvetica-Bold'),
            ('FONTNAME', (0, 19), (0, 19), 'Helvetica-Bold'),
        ]))
        
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