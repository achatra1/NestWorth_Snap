// One-time baby expenses (converted from Excel)
// Source: One Time costs.xlsx

export interface OneTimeExpense {
  item: string;
  category: string;
  lowCost: number;
  averageCost: number;
  highCost: number;
  notes?: string;
}

export const oneTimeExpenses: OneTimeExpense[] = [
  // Nursery Furniture
  {
    item: 'Crib',
    category: 'Nursery Furniture',
    lowCost: 150,
    averageCost: 300,
    highCost: 800,
    notes: 'Convertible cribs cost more but last longer'
  },
  {
    item: 'Crib Mattress',
    category: 'Nursery Furniture',
    lowCost: 80,
    averageCost: 150,
    highCost: 300,
  },
  {
    item: 'Changing Table',
    category: 'Nursery Furniture',
    lowCost: 80,
    averageCost: 120,
    highCost: 250,
  },
  {
    item: 'Dresser',
    category: 'Nursery Furniture',
    lowCost: 150,
    averageCost: 250,
    highCost: 500,
  },
  {
    item: 'Rocking Chair/Glider',
    category: 'Nursery Furniture',
    lowCost: 150,
    averageCost: 300,
    highCost: 600,
  },
  
  // Transportation
  {
    item: 'Car Seat (Infant)',
    category: 'Transportation',
    lowCost: 100,
    averageCost: 200,
    highCost: 400,
    notes: 'Rear-facing for infants'
  },
  {
    item: 'Stroller',
    category: 'Transportation',
    lowCost: 100,
    averageCost: 250,
    highCost: 800,
    notes: 'Travel systems cost more'
  },
  {
    item: 'Baby Carrier',
    category: 'Transportation',
    lowCost: 30,
    averageCost: 80,
    highCost: 200,
  },
  
  // Feeding
  {
    item: 'High Chair',
    category: 'Feeding',
    lowCost: 50,
    averageCost: 150,
    highCost: 300,
  },
  {
    item: 'Bottles & Accessories',
    category: 'Feeding',
    lowCost: 50,
    averageCost: 100,
    highCost: 200,
  },
  {
    item: 'Breast Pump',
    category: 'Feeding',
    lowCost: 50,
    averageCost: 200,
    highCost: 400,
    notes: 'Often covered by insurance'
  },
  
  // Safety & Monitoring
  {
    item: 'Baby Monitor',
    category: 'Safety & Monitoring',
    lowCost: 50,
    averageCost: 100,
    highCost: 300,
    notes: 'Video monitors cost more'
  },
  {
    item: 'Baby Gates',
    category: 'Safety & Monitoring',
    lowCost: 40,
    averageCost: 80,
    highCost: 150,
    notes: 'May need multiple gates'
  },
  
  // Bathing
  {
    item: 'Baby Bathtub',
    category: 'Bathing',
    lowCost: 15,
    averageCost: 30,
    highCost: 60,
  },
  
  // Bedding & Decor
  {
    item: 'Crib Bedding Set',
    category: 'Bedding & Decor',
    lowCost: 50,
    averageCost: 100,
    highCost: 200,
  },
  {
    item: 'Nursery Decor',
    category: 'Bedding & Decor',
    lowCost: 50,
    averageCost: 150,
    highCost: 500,
  },
  
  // Other Essentials
  {
    item: 'Diaper Bag',
    category: 'Other Essentials',
    lowCost: 30,
    averageCost: 60,
    highCost: 150,
  },
  {
    item: 'Play Mat/Gym',
    category: 'Other Essentials',
    lowCost: 30,
    averageCost: 60,
    highCost: 120,
  },
  {
    item: 'Swing/Bouncer',
    category: 'Other Essentials',
    lowCost: 50,
    averageCost: 100,
    highCost: 250,
  },
];

// Helper function to get total one-time costs by cost level
export function getTotalOneTimeCosts(costLevel: 'low' | 'average' | 'high'): number {
  return oneTimeExpenses.reduce((total, expense) => {
    switch (costLevel) {
      case 'low':
        return total + expense.lowCost;
      case 'high':
        return total + expense.highCost;
      default:
        return total + expense.averageCost;
    }
  }, 0);
}

// Helper function to get one-time costs by category
export function getOneTimeCostsByCategory(costLevel: 'low' | 'average' | 'high'): Record<string, number> {
  const categories: Record<string, number> = {};
  
  oneTimeExpenses.forEach(expense => {
    if (!categories[expense.category]) {
      categories[expense.category] = 0;
    }
    
    switch (costLevel) {
      case 'low':
        categories[expense.category] += expense.lowCost;
        break;
      case 'high':
        categories[expense.category] += expense.highCost;
        break;
      default:
        categories[expense.category] += expense.averageCost;
    }
  });
  
  return categories;
}

// Essential items for MVP (subset of all items)
export const essentialOneTimeItems = [
  'Crib',
  'Crib Mattress',
  'Changing Table',
  'Car Seat (Infant)',
  'Stroller',
  'High Chair',
  'Baby Monitor',
  'Bottles & Accessories',
];

export function getEssentialOneTimeCosts(costLevel: 'low' | 'average' | 'high'): Record<string, number> {
  const costs: Record<string, number> = {};
  
  oneTimeExpenses
    .filter(expense => essentialOneTimeItems.includes(expense.item))
    .forEach(expense => {
      switch (costLevel) {
        case 'low':
          costs[expense.item] = expense.lowCost;
          break;
        case 'high':
          costs[expense.item] = expense.highCost;
          break;
        default:
          costs[expense.item] = expense.averageCost;
      }
    });
  
  return costs;
}