import { ExpenseAssumptions, UserFinancialProfile } from '@/types/financial';
import { 
  getChildcareCostByZip, 
  averageChildcareCosts, 
  weeklyToMonthlyCost 
} from '@/data/childcareCostsByZip';
import { getEssentialOneTimeCosts } from '@/data/oneTimeCosts';
import { getMonthlyRecurringCosts } from '@/data/recurringCosts';

// Determine cost level based on childcare costs (as a proxy for regional cost)
function determineCostLevel(weeklyInfantCost: number): 'low' | 'medium' | 'high' {
  if (weeklyInfantCost < 280) return 'low';
  if (weeklyInfantCost > 400) return 'high';
  return 'medium';
}

export function getBabyExpenseAssumptions(
  profile: UserFinancialProfile
): ExpenseAssumptions {
  // Get childcare costs from reference data
  const childcareData = getChildcareCostByZip(profile.zipCode);
  
  // Use actual data if available, otherwise use averages
  const weeklyInfantCost = childcareData?.weeklyInfantCost || averageChildcareCosts.weeklyInfantCost;
  const weeklyToddlerCost = childcareData?.weeklyToddlerCost || averageChildcareCosts.weeklyToddlerCost;
  
  // Determine cost band based on childcare costs
  const costBand = determineCostLevel(weeklyInfantCost);
  
  // Get one-time costs from reference data
  const oneTimeCostsData = getEssentialOneTimeCosts(costBand === 'low' ? 'low' : costBand === 'high' ? 'high' : 'average');
  
  // Get recurring costs for a newborn (month 0) from reference data
  const recurringCostsMonth0 = getMonthlyRecurringCosts(0, costBand === 'low' ? 'low' : costBand === 'high' ? 'high' : 'average');
  
  return {
    costBand,
    oneTimeCosts: {
      crib: oneTimeCostsData['Crib'] || 300,
      stroller: oneTimeCostsData['Stroller'] || 250,
      carSeat: oneTimeCostsData['Car Seat (Infant)'] || 200,
      highChair: oneTimeCostsData['High Chair'] || 150,
      babyMonitor: oneTimeCostsData['Baby Monitor'] || 100,
      changingTable: oneTimeCostsData['Changing Table'] || 120,
    },
    monthlyRecurring: {
      diapers: recurringCostsMonth0['Diapers & Wipes'] || 105,
      wipes: 0, // Included in diapers category
      formula: recurringCostsMonth0['Formula & Food'] || 150,
      babyFood: 0, // Starts at month 6
      miscellaneous: recurringCostsMonth0['Miscellaneous'] || 100,
    },
    childcareCosts: {
      daycare: weeklyToMonthlyCost(weeklyInfantCost),
      nanny: weeklyToMonthlyCost(weeklyInfantCost * 1.8), // Nannies typically cost ~1.8x daycare
      stayAtHome: 0,
    },
    childcareStartMonth: 6,
  };
}

export function getAssumptionExplanations(assumptions: ExpenseAssumptions): string[] {
  return [
    `Regional Cost Band: ${assumptions.costBand.toUpperCase()} - Based on your ZIP code, we've adjusted costs to reflect your local market using reference data from childcare cost surveys.`,
    `One-Time Costs: Essential items include crib ($${assumptions.oneTimeCosts.crib}), stroller ($${assumptions.oneTimeCosts.stroller}), car seat ($${assumptions.oneTimeCosts.carSeat}), high chair ($${assumptions.oneTimeCosts.highChair}), baby monitor ($${assumptions.oneTimeCosts.babyMonitor}), and changing table ($${assumptions.oneTimeCosts.changingTable}). These are purchased in the first few months.`,
    `Monthly Recurring Costs: Diapers & wipes ($${assumptions.monthlyRecurring.diapers}/mo), formula ($${assumptions.monthlyRecurring.formula}/mo for first year), and miscellaneous expenses ($${assumptions.monthlyRecurring.miscellaneous}/mo). Healthcare and clothing costs are not included in projections.`,
    `Childcare Costs: Based on your ZIP code, ${assumptions.childcareCosts.daycare > 0 ? `daycare costs approximately $${assumptions.childcareCosts.daycare}/month` : ''} ${assumptions.childcareCosts.nanny > 0 ? `and nanny costs approximately $${assumptions.childcareCosts.nanny}/month` : ''}. We assume childcare starts at month ${assumptions.childcareStartMonth}.`,
    `Parental Leave: Income adjustments are calculated based on your specified leave duration and percentage paid.`,
    `Formula Feeding: We assume formula feeding for the first 12 months. Breastfeeding families will have lower costs.`,
    `Age-Based Adjustments: Costs change as baby grows - formula ends at 12 months, solid food starts at 6 months, and diaper usage decreases over time.`,
    `Data Sources: Costs are based on national surveys and regional childcare cost data. Your actual costs may vary based on specific choices and circumstances.`,
  ];
}