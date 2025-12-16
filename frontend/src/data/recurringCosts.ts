// Recurring monthly baby expenses (converted from Excel)
// Source: Recurring costs.xlsx

export interface RecurringExpense {
  item: string;
  category: string;
  lowCost: number;
  averageCost: number;
  highCost: number;
  startMonth: number; // When this expense typically starts (0 = birth)
  endMonth?: number; // When this expense typically ends (undefined = ongoing)
  notes?: string;
}

export const recurringExpenses: RecurringExpense[] = [
  // Diapers & Wipes
  {
    item: 'Diapers',
    category: 'Diapers & Wipes',
    lowCost: 60,
    averageCost: 80,
    highCost: 120,
    startMonth: 0,
    endMonth: 30, // ~2.5 years for potty training
    notes: 'Newborns use 8-12 diapers/day, decreases over time'
  },
  {
    item: 'Wipes',
    category: 'Diapers & Wipes',
    lowCost: 15,
    averageCost: 25,
    highCost: 40,
    startMonth: 0,
    endMonth: 36,
  },
  {
    item: 'Diaper Cream',
    category: 'Diapers & Wipes',
    lowCost: 5,
    averageCost: 10,
    highCost: 20,
    startMonth: 0,
    endMonth: 30,
  },
  
  // Formula & Food
  {
    item: 'Formula',
    category: 'Formula & Food',
    lowCost: 100,
    averageCost: 150,
    highCost: 250,
    startMonth: 0,
    endMonth: 12,
    notes: 'For formula-fed babies; breastfeeding has minimal cost'
  },
  {
    item: 'Baby Food (Purees)',
    category: 'Formula & Food',
    lowCost: 50,
    averageCost: 80,
    highCost: 120,
    startMonth: 6,
    endMonth: 12,
    notes: 'Starts around 6 months'
  },
  {
    item: 'Toddler Food',
    category: 'Formula & Food',
    lowCost: 80,
    averageCost: 120,
    highCost: 180,
    startMonth: 12,
    notes: 'Transition to table foods'
  },
  {
    item: 'Snacks',
    category: 'Formula & Food',
    lowCost: 20,
    averageCost: 40,
    highCost: 60,
    startMonth: 9,
  },
  
  // Clothing
  {
    item: 'Clothing (0-12 months)',
    category: 'Clothing',
    lowCost: 30,
    averageCost: 50,
    highCost: 100,
    startMonth: 0,
    endMonth: 12,
    notes: 'Babies grow quickly, need frequent size changes'
  },
  {
    item: 'Clothing (12-24 months)',
    category: 'Clothing',
    lowCost: 35,
    averageCost: 60,
    highCost: 120,
    startMonth: 12,
    endMonth: 24,
  },
  {
    item: 'Clothing (2-5 years)',
    category: 'Clothing',
    lowCost: 40,
    averageCost: 70,
    highCost: 140,
    startMonth: 24,
  },
  
  // Healthcare
  {
    item: 'Medical Co-pays',
    category: 'Healthcare',
    lowCost: 30,
    averageCost: 50,
    highCost: 100,
    startMonth: 0,
    notes: 'Well-child visits, sick visits'
  },
  {
    item: 'Medications & Vitamins',
    category: 'Healthcare',
    lowCost: 10,
    averageCost: 25,
    highCost: 50,
    startMonth: 0,
  },
  {
    item: 'Dental Care',
    category: 'Healthcare',
    lowCost: 0,
    averageCost: 20,
    highCost: 50,
    startMonth: 12,
    notes: 'First dental visit around 12 months'
  },
  
  // Personal Care
  {
    item: 'Bath Products',
    category: 'Personal Care',
    lowCost: 10,
    averageCost: 20,
    highCost: 40,
    startMonth: 0,
  },
  {
    item: 'Laundry (Extra)',
    category: 'Personal Care',
    lowCost: 15,
    averageCost: 30,
    highCost: 50,
    startMonth: 0,
    notes: 'Increased laundry costs'
  },
  
  // Toys & Books
  {
    item: 'Toys',
    category: 'Toys & Books',
    lowCost: 20,
    averageCost: 40,
    highCost: 80,
    startMonth: 3,
  },
  {
    item: 'Books',
    category: 'Toys & Books',
    lowCost: 10,
    averageCost: 20,
    highCost: 40,
    startMonth: 0,
  },
  
  // Miscellaneous
  {
    item: 'Miscellaneous',
    category: 'Miscellaneous',
    lowCost: 50,
    averageCost: 100,
    highCost: 200,
    startMonth: 0,
    notes: 'Unexpected expenses, replacements, etc.'
  },
];

// Helper function to get monthly recurring costs by baby age
export function getMonthlyRecurringCosts(
  babyAgeMonths: number,
  costLevel: 'low' | 'average' | 'high'
): Record<string, number> {
  const costs: Record<string, number> = {};
  
  recurringExpenses.forEach(expense => {
    // Check if expense applies to this age
    if (babyAgeMonths >= expense.startMonth) {
      if (!expense.endMonth || babyAgeMonths <= expense.endMonth) {
        let cost = 0;
        switch (costLevel) {
          case 'low':
            cost = expense.lowCost;
            break;
          case 'high':
            cost = expense.highCost;
            break;
          default:
            cost = expense.averageCost;
        }
        
        if (!costs[expense.category]) {
          costs[expense.category] = 0;
        }
        costs[expense.category] += cost;
      }
    }
  });
  
  return costs;
}

// Helper function to get total monthly recurring costs
export function getTotalMonthlyRecurringCosts(
  babyAgeMonths: number,
  costLevel: 'low' | 'average' | 'high'
): number {
  const costs = getMonthlyRecurringCosts(babyAgeMonths, costLevel);
  return Object.values(costs).reduce((total, cost) => total + cost, 0);
}

// Get average costs across all months for summary
export function getAverageMonthlyRecurringCosts(costLevel: 'low' | 'average' | 'high'): number {
  let totalCost = 0;
  const months = 60; // 5 years
  
  for (let month = 0; month < months; month++) {
    totalCost += getTotalMonthlyRecurringCosts(month, costLevel);
  }
  
  return Math.round(totalCost / months);
}