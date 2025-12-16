"""
Loader for childcare cost reference data from Excel file.
Loads data from 'Ref Data Childcare cost byZip.xlsx' and provides lookup functions.
"""

import os
from typing import Dict, List, Optional, Literal
import pandas as pd
from functools import lru_cache


# Path to the Excel file (relative to project root)
EXCEL_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'Ref Data Childcare cost byZip.xlsx'
)


class ChildcareCostData:
    """Container for childcare cost data loaded from Excel."""
    
    def __init__(self):
        self._data: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self):
        """Load childcare cost data from Excel file."""
        try:
            if os.path.exists(EXCEL_FILE_PATH):
                # Read the Excel file
                self._data = pd.read_excel(EXCEL_FILE_PATH)
                print(f"✓ Loaded childcare cost data: {len(self._data)} ZIP codes")
            else:
                print(f"⚠ Warning: Childcare cost file not found at {EXCEL_FILE_PATH}")
                print("  Using fallback hardcoded data")
                self._data = None
        except Exception as e:
            print(f"⚠ Error loading childcare cost data: {e}")
            print("  Using fallback hardcoded data")
            self._data = None
    
    def get_cost_by_zip(
        self,
        zip_code: str,
        scenario: Literal['daycare', 'nanny', 'stay-at-home']
    ) -> Optional[Dict[str, float]]:
        """
        Get childcare costs for a specific ZIP code and scenario.
        
        Args:
            zip_code: 5-digit ZIP code
            scenario: 'daycare', 'nanny', or 'stay-at-home'
        
        Returns:
            Dictionary with weekly costs by age group, or None if not found
        """
        if self._data is None:
            return None
        
        # Try exact match first
        matches = self._data[self._data['ZIP'].astype(str).str.zfill(5) == zip_code.zfill(5)]
        
        # If no exact match, try 3-digit prefix
        if matches.empty:
            prefix = zip_code[:3]
            matches = self._data[self._data['ZIP'].astype(str).str.zfill(5).str.startswith(prefix)]
        
        if matches.empty:
            return None
        
        # Get the first match
        row = matches.iloc[0]
        
        # Map scenario to column names
        # Assuming columns are named like: "Center Infant", "Center Toddler", "Center Preschool"
        # or "Home Infant", "Home Toddler", "Home Preschool"
        if scenario == 'daycare':
            prefix = 'Center'
        elif scenario == 'nanny':
            prefix = 'Home'  # Home-based care (nanny/family care)
        else:  # stay-at-home
            return {
                'infant': 0,
                'toddler': 0,
                'preschool': 0,
                'state': row.get('State', ''),
                'city': row.get('County', '')
            }
        
        # Extract costs (handle different possible column naming conventions)
        result = {}
        
        # Try different column name patterns
        for age_group in ['Infant', 'Toddler', 'Preschool']:
            col_name = None
            # Try various column name formats
            possible_names = [
                f'{prefix} {age_group}',
                f'{prefix}_{age_group}',
                f'{prefix}{age_group}',
                age_group if scenario == 'daycare' else f'Home_{age_group}'
            ]
            
            for name in possible_names:
                if name in row.index:
                    col_name = name
                    break
            
            if col_name and pd.notna(row[col_name]):
                result[age_group.lower()] = float(row[col_name])
            else:
                result[age_group.lower()] = 0
        
        # Add location info
        result['state'] = row.get('State', row.get('STATE', ''))
        result['city'] = row.get('County', row.get('COUNTY', ''))
        
        return result
    
    def get_all_zip_codes(self) -> List[str]:
        """Get list of all available ZIP codes."""
        if self._data is None:
            return []
        return self._data['ZIP'].astype(str).str.zfill(5).tolist()


# Global instance (loaded once at startup)
_childcare_data = None


@lru_cache(maxsize=1)
def get_childcare_data() -> ChildcareCostData:
    """Get the global childcare data instance (cached)."""
    global _childcare_data
    if _childcare_data is None:
        _childcare_data = ChildcareCostData()
    return _childcare_data


def get_childcare_cost_by_zip(
    zip_code: str,
    scenario: Literal['daycare', 'nanny', 'stay-at-home']
) -> Optional[Dict[str, float]]:
    """
    Convenience function to get childcare costs by ZIP code and scenario.
    
    Args:
        zip_code: 5-digit ZIP code
        scenario: 'daycare', 'nanny', or 'stay-at-home'
    
    Returns:
        Dictionary with weekly costs, or None if not found
    """
    data = get_childcare_data()
    return data.get_cost_by_zip(zip_code, scenario)