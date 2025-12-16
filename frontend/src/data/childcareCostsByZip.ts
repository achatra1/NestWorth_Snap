// Weekly childcare costs by ZIP code (converted from Excel)
// Source: Ref Data Childcare cost byZip.xlsx

export interface ChildcareCostByZip {
  zipCode: string;
  weeklyInfantCost: number;
  weeklyToddlerCost: number;
  weeklyPreschoolCost: number;
  state: string;
  city?: string;
}

// Sample data structure - you'll need to populate this with actual Excel data
export const childcareCostsByZip: ChildcareCostByZip[] = [
  // High-cost areas (examples)
  { zipCode: '10001', weeklyInfantCost: 450, weeklyToddlerCost: 400, weeklyPreschoolCost: 350, state: 'NY', city: 'New York' },
  { zipCode: '10002', weeklyInfantCost: 445, weeklyToddlerCost: 395, weeklyPreschoolCost: 345, state: 'NY', city: 'New York' },
  { zipCode: '94102', weeklyInfantCost: 480, weeklyToddlerCost: 430, weeklyPreschoolCost: 380, state: 'CA', city: 'San Francisco' },
  { zipCode: '90001', weeklyInfantCost: 420, weeklyToddlerCost: 370, weeklyPreschoolCost: 320, state: 'CA', city: 'Los Angeles' },
  { zipCode: '98101', weeklyInfantCost: 440, weeklyToddlerCost: 390, weeklyPreschoolCost: 340, state: 'WA', city: 'Seattle' },
  { zipCode: '02101', weeklyInfantCost: 460, weeklyToddlerCost: 410, weeklyPreschoolCost: 360, state: 'MA', city: 'Boston' },
  { zipCode: '20001', weeklyInfantCost: 430, weeklyToddlerCost: 380, weeklyPreschoolCost: 330, state: 'DC', city: 'Washington' },
  
  // Medium-cost areas (examples)
  { zipCode: '60601', weeklyInfantCost: 350, weeklyToddlerCost: 310, weeklyPreschoolCost: 270, state: 'IL', city: 'Chicago' },
  { zipCode: '75201', weeklyInfantCost: 320, weeklyToddlerCost: 280, weeklyPreschoolCost: 240, state: 'TX', city: 'Dallas' },
  { zipCode: '30301', weeklyInfantCost: 330, weeklyToddlerCost: 290, weeklyPreschoolCost: 250, state: 'GA', city: 'Atlanta' },
  { zipCode: '85001', weeklyInfantCost: 310, weeklyToddlerCost: 270, weeklyPreschoolCost: 230, state: 'AZ', city: 'Phoenix' },
  { zipCode: '33101', weeklyInfantCost: 340, weeklyToddlerCost: 300, weeklyPreschoolCost: 260, state: 'FL', city: 'Miami' },
  
  // Low-cost areas (examples)
  { zipCode: '35004', weeklyInfantCost: 240, weeklyToddlerCost: 210, weeklyPreschoolCost: 180, state: 'AL', city: 'Birmingham' },
  { zipCode: '38601', weeklyInfantCost: 230, weeklyToddlerCost: 200, weeklyPreschoolCost: 170, state: 'MS', city: 'Jackson' },
  { zipCode: '71601', weeklyInfantCost: 250, weeklyToddlerCost: 220, weeklyPreschoolCost: 190, state: 'AR', city: 'Little Rock' },
  { zipCode: '50301', weeklyInfantCost: 260, weeklyToddlerCost: 230, weeklyPreschoolCost: 200, state: 'IA', city: 'Des Moines' },
];

// Helper function to get childcare cost by ZIP code
export function getChildcareCostByZip(zipCode: string): ChildcareCostByZip | null {
  // Try exact match first
  const exactMatch = childcareCostsByZip.find(c => c.zipCode === zipCode);
  if (exactMatch) return exactMatch;
  
  // Try matching first 3 digits (ZIP code prefix)
  const prefix = zipCode.substring(0, 3);
  const prefixMatch = childcareCostsByZip.find(c => c.zipCode.startsWith(prefix));
  if (prefixMatch) return prefixMatch;
  
  return null;
}

// Calculate average costs for fallback
export const averageChildcareCosts = {
  weeklyInfantCost: 340,
  weeklyToddlerCost: 300,
  weeklyPreschoolCost: 260,
};

// Convert weekly to monthly (multiply by 4.33 weeks per month)
export function weeklyToMonthlyCost(weeklyCost: number): number {
  return Math.round(weeklyCost * 4.33);
}