"""
Loader for recurring costs from Excel file.
"""

import os
from typing import Dict, Optional
import openpyxl


def get_recurring_costs() -> Dict[str, float]:
    """
    Load recurring costs from Excel file.
    Returns a dictionary with item names as keys and monthly costs as values.
    """
    # Get the path to the Excel file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    excel_path = os.path.join(project_root, '..', 'Recurring costs.xlsx')
    
    # Normalize the path
    excel_path = os.path.normpath(excel_path)
    
    if not os.path.exists(excel_path):
        print(f"Warning: Recurring costs Excel file not found at {excel_path}")
        return get_default_recurring_costs()
    
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(excel_path, data_only=True)
        sheet = workbook.active
        
        costs = {}
        
        # Skip header row, start from row 2
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] and row[1]:  # Both item and cost must be present
                item = str(row[0]).strip()
                try:
                    cost = float(row[1])
                    costs[item] = cost
                except (ValueError, TypeError):
                    print(f"Warning: Could not parse cost for {item}: {row[1]}")
                    continue
        
        workbook.close()
        
        if not costs:
            print("Warning: No recurring costs found in Excel file, using defaults")
            return get_default_recurring_costs()
        
        return costs
        
    except Exception as e:
        print(f"Error loading recurring costs from Excel: {e}")
        return get_default_recurring_costs()


def get_default_recurring_costs() -> Dict[str, float]:
    """
    Return default recurring costs if Excel file cannot be loaded.
    """
    return {
        'Diaper': 80,
        'Wipes': 15,
        'Food': 150,
        'Supplies': 25,
        'Toys': 20,
        'Miscellaneous ( Activities, Baby sitter etc)': 150,
    }


# Cache the costs on module load
_RECURRING_COSTS = get_recurring_costs()


def get_monthly_recurring_costs(year: int) -> Dict[str, float]:
    """
    Get monthly recurring costs for a given year.
    Miscellaneous increases by 20% from Year 3 onward (each year).
    
    Args:
        year: The year number (1-5)
    
    Returns:
        Dictionary with item names and their monthly costs
    """
    costs = _RECURRING_COSTS.copy()
    
    # Apply 20% increase to Miscellaneous from Year 3 onward
    if year >= 3:
        misc_key = 'Miscellaneous ( Activities, Baby sitter etc)'
        if misc_key in costs:
            # Increase by 20% for each year starting from year 3
            # Year 3: 1.2x, Year 4: 1.44x (1.2^2), Year 5: 1.728x (1.2^3)
            multiplier = 1.2 ** (year - 2)
            costs[misc_key] = costs[misc_key] * multiplier
    
    return costs