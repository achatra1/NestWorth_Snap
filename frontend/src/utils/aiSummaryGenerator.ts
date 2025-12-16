import { FiveYearProjection } from '@/types/financial';

export function generateAISummary(projection: FiveYearProjection): string {
  const { profile, yearlyProjections, totalCost, warnings, assumptions } = projection;
  
  // Calculate key metrics
  const totalIncome = yearlyProjections.reduce((sum, y) => sum + y.totalIncome, 0);
  const totalChildcareCost = yearlyProjections.reduce((sum, y) => sum + y.expenseBreakdown.childcare, 0);
  const oneTimeCosts = yearlyProjections.reduce((sum, y) => sum + y.expenseBreakdown.oneTime, 0);
  const recurringCosts = totalCost - oneTimeCosts;
  
  const householdIncome = (profile.partner1Income + profile.partner2Income) * 12;
  const babyCostAsPercentOfIncome = (totalCost / totalIncome) * 100;
  
  // Build structured summary
  let summary = `# 5-Year Baby Budget Blueprint\n\n`;
  
  // Executive Summary
  summary += `## Executive Summary\n\n`;
  summary += `**Total 5-Year Baby Costs**: ${formatCurrency(totalCost)}\n\n`;
  summary += `**Household Annual Income**: ${formatCurrency(householdIncome)}\n\n`;
  summary += `**Baby Costs as % of 5-Year Income**: ${babyCostAsPercentOfIncome.toFixed(1)}%\n\n`;
  
  summary += `| Metric | Amount |\n`;
  summary += `|--------|--------|\n`;
  summary += `| One-Time Costs | ${formatCurrency(oneTimeCosts)} |\n`;
  summary += `| Recurring Costs (5 years) | ${formatCurrency(recurringCosts)} |\n`;
  summary += `| Total Childcare (5 years) | ${formatCurrency(totalChildcareCost)} |\n`;
  summary += `| Average Annual Cost | ${formatCurrency(totalCost / 5)} |\n`;
  summary += `| Average Monthly Cost | ${formatCurrency(totalCost / 60)} |\n\n`;
  
  // Life Stage Breakdown
  summary += `## Life Stage Breakdown\n\n`;
  
  // Year 0-1 (Infant)
  const year1 = yearlyProjections[0];
  const year1ChildcarePercent = (year1.expenseBreakdown.childcare / year1.totalIncome) * 100;
  summary += `### Year 0-1: Newborn/Infant Stage\n\n`;
  summary += `**Total Cost**: ${formatCurrency(year1.totalExpenses)}\n\n`;
  summary += `**Monthly Average**: ${formatCurrency(year1.totalExpenses / 12)}\n\n`;
  summary += `**Key Drivers**:\n`;
  summary += `- One-time purchases: ${formatCurrency(year1.expenseBreakdown.oneTime)} (crib, stroller, car seat, nursery setup)\n`;
  summary += `- Formula/feeding: ${formatCurrency(year1.expenseBreakdown.food)}\n`;
  summary += `- Diapers: ${formatCurrency(year1.expenseBreakdown.diapers)}\n`;
  summary += `- Childcare: ${formatCurrency(year1.expenseBreakdown.childcare)} (${year1ChildcarePercent.toFixed(1)}% of income)\n\n`;
  
  if (year1.expenseBreakdown.oneTime > 0) {
    summary += `*Note: Year 1 includes significant one-time purchases. These costs won't repeat.*\n\n`;
  }
  
  // Year 1-3 (Toddler)
  const year2 = yearlyProjections[1];
  const year3 = yearlyProjections[2];
  const toddlerTotal = year2.totalExpenses + year3.totalExpenses;
  const toddlerChildcare = year2.expenseBreakdown.childcare + year3.expenseBreakdown.childcare;
  const toddlerIncome = year2.totalIncome + year3.totalIncome;
  const toddlerChildcarePercent = (toddlerChildcare / toddlerIncome) * 100;
  
  summary += `### Year 1-3: Toddler Stage\n\n`;
  summary += `**Total Cost (2 years)**: ${formatCurrency(toddlerTotal)}\n\n`;
  summary += `**Monthly Average**: ${formatCurrency(toddlerTotal / 24)}\n\n`;
  summary += `**Key Drivers**:\n`;
  summary += `- Childcare: ${formatCurrency(toddlerChildcare)} (${toddlerChildcarePercent.toFixed(1)}% of income)\n`;
  summary += `- Food (solid foods): ${formatCurrency(year2.expenseBreakdown.food + year3.expenseBreakdown.food)}\n`;
  summary += `- Clothing (growing fast): ${formatCurrency(year2.expenseBreakdown.clothing + year3.expenseBreakdown.clothing)}\n`;
  summary += `- Healthcare: ${formatCurrency(year2.expenseBreakdown.healthcare + year3.expenseBreakdown.healthcare)}\n\n`;
  
  if (profile.childcarePreference !== 'stay-at-home') {
    summary += `*Note: Childcare is your largest recurring expense during this period.*\n\n`;
  }
  
  // Year 3-5 (Preschool)
  const year4 = yearlyProjections[3];
  const year5 = yearlyProjections[4];
  const preschoolTotal = year4.totalExpenses + year5.totalExpenses;
  const preschoolChildcare = year4.expenseBreakdown.childcare + year5.expenseBreakdown.childcare;
  const preschoolIncome = year4.totalIncome + year5.totalIncome;
  const preschoolChildcarePercent = (preschoolChildcare / preschoolIncome) * 100;
  
  summary += `### Year 3-5: Preschool Stage\n\n`;
  summary += `**Total Cost (2 years)**: ${formatCurrency(preschoolTotal)}\n\n`;
  summary += `**Monthly Average**: ${formatCurrency(preschoolTotal / 24)}\n\n`;
  summary += `**Key Drivers**:\n`;
  summary += `- Childcare: ${formatCurrency(preschoolChildcare)} (${preschoolChildcarePercent.toFixed(1)}% of income)\n`;
  summary += `- Food (increased appetite): ${formatCurrency(year4.expenseBreakdown.food + year5.expenseBreakdown.food)}\n`;
  summary += `- Clothing (larger sizes): ${formatCurrency(year4.expenseBreakdown.clothing + year5.expenseBreakdown.clothing)}\n`;
  summary += `- Activities/supplies: ${formatCurrency(year4.expenseBreakdown.miscellaneous + year5.expenseBreakdown.miscellaneous)}\n\n`;
  
  summary += `*Note: Diaper costs decrease/end during this period as potty training completes.*\n\n`;
  
  // Childcare Analysis
  summary += `## Childcare Analysis\n\n`;
  summary += `**Your Selection**: ${capitalizeFirst(profile.childcarePreference)}\n\n`;
  
  if (profile.childcarePreference !== 'stay-at-home') {
    const monthlyChildcareCost = profile.childcarePreference === 'daycare' 
      ? assumptions.childcareCosts.daycare 
      : assumptions.childcareCosts.nanny;
    
    const childcareAsPercentOfHouseholdIncome = (monthlyChildcareCost / (profile.partner1Income + profile.partner2Income)) * 100;
    const childcareAsPercentOfPartner1Income = (monthlyChildcareCost / profile.partner1Income) * 100;
    
    summary += `**Monthly Cost**: ${formatCurrency(monthlyChildcareCost)}\n\n`;
    summary += `**Annual Cost**: ${formatCurrency(monthlyChildcareCost * 12)}\n\n`;
    summary += `**5-Year Total**: ${formatCurrency(totalChildcareCost)}\n\n`;
    summary += `**As % of Household Income**: ${childcareAsPercentOfHouseholdIncome.toFixed(1)}%\n\n`;
    summary += `**As % of Partner 1 Income**: ${childcareAsPercentOfPartner1Income.toFixed(1)}%\n\n`;
    
    if (childcareAsPercentOfHouseholdIncome > 25) {
      summary += `⚠️ **Financial Pressure Point**: Childcare exceeds 25% of household income. This is significant but not uncommon in your area.\n\n`;
    }
    
    summary += `*Assumption: Childcare starts at month ${assumptions.childcareStartMonth}. Costs based on ${assumptions.costBand}-cost area (ZIP ${profile.zipCode}).*\n\n`;
  } else {
    summary += `**Monthly Cost**: $0 (direct cost)\n\n`;
    summary += `**5-Year Total**: $0\n\n`;
    summary += `*Note: Stay-at-home parenting has no direct childcare cost, but represents an opportunity cost in terms of foregone income. This analysis focuses on direct baby-related expenses only.*\n\n`;
  }
  
  // One-Time vs Recurring
  summary += `## Cost Structure\n\n`;
  summary += `| Category | Amount | % of Total |\n`;
  summary += `|----------|--------|------------|\n`;
  summary += `| One-Time Costs | ${formatCurrency(oneTimeCosts)} | ${((oneTimeCosts / totalCost) * 100).toFixed(1)}% |\n`;
  summary += `| Recurring Costs | ${formatCurrency(recurringCosts)} | ${((recurringCosts / totalCost) * 100).toFixed(1)}% |\n`;
  summary += `| **Total** | **${formatCurrency(totalCost)}** | **100%** |\n\n`;
  
  summary += `**One-Time Costs** (Month 0-2):\n`;
  summary += `- Nursery furniture: Crib ($${assumptions.oneTimeCosts.crib}), changing table ($${assumptions.oneTimeCosts.changingTable})\n`;
  summary += `- Transportation: Car seat ($${assumptions.oneTimeCosts.carSeat}), stroller ($${assumptions.oneTimeCosts.stroller})\n`;
  summary += `- Feeding: High chair ($${assumptions.oneTimeCosts.highChair})\n`;
  summary += `- Safety: Baby monitor ($${assumptions.oneTimeCosts.babyMonitor})\n\n`;
  
  summary += `**Recurring Monthly Costs** (vary by age):\n`;
  summary += `- Diapers & wipes (months 0-30)\n`;
  summary += `- Formula (months 0-12)\n`;
  summary += `- Baby food (months 6+)\n`;
  summary += `- Clothing (ongoing, sizes change)\n`;
  summary += `- Healthcare (co-pays, medications)\n`;
  summary += `- Childcare (month ${assumptions.childcareStartMonth}+)\n\n`;
  
  // Financial Pressure Points
  summary += `## Financial Pressure Points\n\n`;
  
  const pressurePoints: string[] = [];
  
  // Check each year for high childcare costs
  yearlyProjections.forEach((year, idx) => {
    const childcarePercent = (year.expenseBreakdown.childcare / year.totalIncome) * 100;
    if (childcarePercent > 25) {
      pressurePoints.push(`**Year ${year.year}**: Childcare represents ${childcarePercent.toFixed(1)}% of income (${formatCurrency(year.expenseBreakdown.childcare)})`);
    }
  });
  
  // Check for negative cashflow
  const negativeMonths = projection.monthlyProjections.filter(m => m.netCashflow < 0);
  if (negativeMonths.length > 0) {
    pressurePoints.push(`**Months ${negativeMonths[0].month}-${negativeMonths[negativeMonths.length - 1].month}**: Potential negative cashflow periods`);
  }
  
  // Check parental leave impact
  const totalLeaveWeeks = profile.partner1Leave.durationWeeks + profile.partner2Leave.durationWeeks;
  if (totalLeaveWeeks > 0) {
    const avgPaidPercent = (profile.partner1Leave.percentPaid + profile.partner2Leave.percentPaid) / 2;
    if (avgPaidPercent < 100) {
      pressurePoints.push(`**Months 0-${Math.ceil(totalLeaveWeeks / 4.33)}**: Reduced income during parental leave (${avgPaidPercent.toFixed(0)}% average pay)`);
    }
  }
  
  if (pressurePoints.length > 0) {
    pressurePoints.forEach(point => {
      summary += `${point}\n\n`;
    });
  } else {
    summary += `No major financial pressure points identified. Your income comfortably covers projected baby expenses.\n\n`;
  }
  
  // Planning Insights
  summary += `## Planning Insights\n\n`;
  
  const insights: string[] = [];
  
  // Insight 1: Emergency fund
  const endingSavings = yearlyProjections[4].endingSavings;
  const savingsChange = endingSavings - profile.currentSavings;
  if (savingsChange < 0) {
    insights.push(`**Build Your Emergency Fund**: Your savings will decrease by ${formatCurrency(Math.abs(savingsChange))} over 5 years. Aim to increase your emergency fund to 3-6 months of expenses before baby arrives.`);
  } else {
    insights.push(`**Strong Savings Position**: You'll end with ${formatCurrency(endingSavings)} in savings, an increase of ${formatCurrency(savingsChange)}. Consider directing some of this toward a 529 education savings plan.`);
  }
  
  // Insight 2: Childcare strategy
  if (profile.childcarePreference !== 'stay-at-home') {
    const monthlyChildcareCost = profile.childcarePreference === 'daycare' 
      ? assumptions.childcareCosts.daycare 
      : assumptions.childcareCosts.nanny;
    const childcarePercent = (monthlyChildcareCost / (profile.partner1Income + profile.partner2Income)) * 100;
    
    if (childcarePercent > 30) {
      insights.push(`**Explore Childcare Options**: At ${childcarePercent.toFixed(1)}% of household income, childcare is your largest expense. Consider flexible work arrangements, family care, or whether one parent staying home might be financially comparable.`);
    } else {
      insights.push(`**Childcare is Manageable**: At ${childcarePercent.toFixed(1)}% of household income, your childcare costs are within typical ranges for your area.`);
    }
  }
  
  // Insight 3: First year costs
  const firstYearPercent = (year1.totalExpenses / totalCost) * 100;
  insights.push(`**Front-Load Your Savings**: Year 1 represents ${firstYearPercent.toFixed(1)}% of your 5-year costs due to one-time purchases. Having ${formatCurrency(year1.expenseBreakdown.oneTime)} available for initial setup will reduce financial stress.`);
  
  // Insight 4: Cost trajectory
  const year1Monthly = year1.totalExpenses / 12;
  const year5Monthly = yearlyProjections[4].totalExpenses / 12;
  if (year5Monthly < year1Monthly) {
    insights.push(`**Costs Decrease Over Time**: Monthly costs drop from ${formatCurrency(year1Monthly)} (Year 1) to ${formatCurrency(year5Monthly)} (Year 5) as one-time purchases end and some recurring costs (diapers, formula) phase out.`);
  }
  
  // Insight 5: Tax benefits
  if (profile.childcarePreference !== 'stay-at-home') {
    insights.push(`**Leverage Tax Benefits**: You may qualify for the Child Tax Credit ($2,000/year) and Dependent Care FSA (up to $5,000/year pre-tax for childcare). These aren't included in this projection but can reduce your effective costs.`);
  }
  
  insights.forEach((insight, idx) => {
    summary += `${idx + 1}. ${insight}\n\n`;
  });
  
  // Assumptions
  summary += `## Key Assumptions\n\n`;
  summary += `- **Location**: ZIP ${profile.zipCode} (${assumptions.costBand}-cost area)\n`;
  summary += `- **Childcare Start**: Month ${assumptions.childcareStartMonth}\n`;
  summary += `- **Formula Feeding**: Assumed for months 0-12 (breastfeeding families will have lower costs)\n`;
  summary += `- **Diaper Usage**: Assumed through month 30 (potty training timeline varies)\n`;
  summary += `- **Healthcare**: Co-pays and OTC medications only (insurance premiums assumed in take-home pay)\n`;
  summary += `- **Inflation**: Costs held constant (conservative assumption)\n`;
  summary += `- **One-Time Purchases**: Essential items only (crib, car seat, stroller, etc.)\n`;
  summary += `- **Housing**: Current housing costs maintained (no move assumed)\n\n`;
  
  // Disclaimer
  summary += `---\n\n`;
  summary += `## Important Disclaimer\n\n`;
  summary += `This budget blueprint is based on your specific inputs and national/regional cost data. Actual costs will vary based on your choices, location, and circumstances. This is not financial advice. Consider consulting a financial advisor for personalized guidance.\n\n`;
  summary += `**What's Not Included**: Health insurance premiums (assumed in take-home pay), college savings, life insurance, will/estate planning, baby gear beyond essentials, photography/keepsakes, travel with baby.\n\n`;
  summary += `**Planning Horizon**: This analysis covers years 0-5. Costs continue beyond age 5 (K-12 education, activities, etc.).`;
  
  return summary;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function capitalizeFirst(str: string): string {
  return str.split('-').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
}