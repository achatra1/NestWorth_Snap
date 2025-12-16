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
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title
    elements.append(Paragraph("NestWorth Financial Plan", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", section_style))
    
    profile = projection.get('profile', {})
    total_cost = projection.get('totalCost', 0)
    yearly_projections = projection.get('yearlyProjections', [])
    
    summary_data = [
        ['Total 5-Year Cost:', format_currency(total_cost)],
        ['Partner 1 Income:', format_currency(profile.get('partner1Income', 0) * 12)],
        ['Partner 2 Income:', format_currency(profile.get('partner2Income', 0) * 12)],
        ['Current Savings:', format_currency(profile.get('currentSavings', 0))],
        ['Childcare Preference:', profile.get('childcarePreference', 'N/A').replace('-', ' ').title()],
    ]
    
    summary_table = Table(summary_data, colWidths=[3 * inch, 2.5 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Year-by-Year Breakdown
    elements.append(Paragraph("Year-by-Year Breakdown", section_style))
    
    yearly_data = [['Year', 'Total Income', 'Total Expenses', 'Net Cashflow', 'Ending Balance']]
    
    for year_proj in yearly_projections:
        year_num = year_proj.get('year', 0)
        total_income = year_proj.get('totalIncome', 0)
        total_expenses = year_proj.get('totalExpenses', 0)
        net_cashflow = year_proj.get('netCashflow', 0)
        ending_balance = year_proj.get('endingBalance', 0)
        
        yearly_data.append([
            f"Year {year_num}",
            format_currency(total_income),
            format_currency(total_expenses),
            format_currency(net_cashflow),
            format_currency(ending_balance)
        ])
    
    yearly_table = Table(yearly_data, colWidths=[1 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    yearly_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(yearly_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Warnings
    warnings = projection.get('warnings', [])
    if warnings:
        elements.append(Paragraph("Important Warnings", section_style))
        
        for warning in warnings:
            severity = warning.get('severity', 'info')
            message = warning.get('message', '')
            
            # Color code by severity
            if severity == 'critical':
                color = colors.red
            elif severity == 'warning':
                color = colors.orange
            else:
                color = colors.blue
            
            warning_style = ParagraphStyle(
                'Warning',
                parent=styles['BodyText'],
                textColor=color,
                leftIndent=20,
                bulletIndent=10
            )
            
            elements.append(Paragraph(f"• {message}", warning_style))
            elements.append(Spacer(1, 0.05 * inch))
        
        elements.append(Spacer(1, 0.2 * inch))
    
    # Page break before AI summary
    elements.append(PageBreak())
    
    # AI Summary
    elements.append(Paragraph("AI Financial Blueprint", section_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    # Parse markdown summary
    summary_elements = parse_markdown_to_paragraphs(summary, styles)
    elements.extend(summary_elements)
    
    # Page break before assumptions
    elements.append(PageBreak())
    
    # Assumptions
    elements.append(Paragraph("Calculation Assumptions", section_style))
    
    assumptions = projection.get('assumptions', {})
    
    assumptions_data = []
    
    # One-time costs
    one_time = assumptions.get('oneTimeCosts', {})
    if one_time:
        assumptions_data.append(['One-Time Costs', ''])
        for key, value in one_time.items():
            label = key.replace('_', ' ').title()
            assumptions_data.append([f"  {label}", format_currency(value)])
    
    # Recurring costs
    recurring = assumptions.get('recurringCosts', {})
    if recurring:
        assumptions_data.append(['Monthly Recurring Costs', ''])
        for key, value in recurring.items():
            label = key.replace('_', ' ').title()
            assumptions_data.append([f"  {label}", format_currency(value)])
    
    # Childcare costs
    childcare = assumptions.get('childcareCosts', {})
    if childcare:
        assumptions_data.append(['Childcare Costs', ''])
        assumptions_data.append([f"  Monthly Cost", format_currency(childcare.get('monthlyCost', 0))])
        assumptions_data.append([f"  Start Month", str(childcare.get('startMonth', 0))])
    
    if assumptions_data:
        assumptions_table = Table(assumptions_data, colWidths=[4 * inch, 2 * inch])
        assumptions_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.grey),
        ]))
        
        elements.append(assumptions_table)
    
    # Build PDF
    doc.build(elements)
    
    # Reset buffer position to beginning
    buffer.seek(0)
    
    return buffer