import {
  UserFinancialProfile,
  ExpenseAssumptions,
  MonthlyProjection,
  YearlyProjection,
  FiveYearProjection,
  Warning,
} from '@/types/financial';
import { getBabyExpenseAssumptions } from './expenseAssumptions';
import { getMonthlyRecurringCosts } from '@/data/recurringCosts';

export function calculateFiveYearProjection(
  profile: UserFinancialProfile
): FiveYearProjection {
  const assumptions = getBabyExpenseAssumptions(profile);
  const monthlyProjections: MonthlyProjection[] = [];
  
  let cumulativeSavings = profile.currentSavings;
  const dueDate = new Date(profile.dueDate);
  
  // Determine cost level for recurring costs
  const costLevel = assumptions.costBand === 'low' ? 'low' : assumptions.costBand === 'high' ? 'high' : 'average';
  
  // Calculate 60 months (5 years)
  for (let month = 1; month <= 60; month++) {
    const year = Math.ceil(month / 12);
    const monthOfYear = ((month - 1) % 12) + 1;
    const babyAgeMonths = month - 1; // Month 1 = baby is 0 months old
    
    // Calculate income (accounting for parental leave)
    const partner1Income = calculateIncomeWithLeave(
      profile.partner1Income,
      babyAgeMonths,
      profile.partner1Leave
    );
    const partner2Income = calculateIncomeWithLeave(
      profile.partner2Income,
      babyAgeMonths,
      profile.partner2Leave
    );
    const totalIncome = partner1Income + partner2Income;
    
    // Calculate expenses using reference data
    const expenses = calculateMonthlyExpenses(
      babyAgeMonths,
      profile,
      assumptions,
      costLevel
    );
    
    const netCashflow = totalIncome - expenses.total;
    cumulativeSavings += netCashflow;
    
    monthlyProjections.push({
      month,
      year,
      monthOfYear,
      income: {
        partner1: partner1Income,
        partner2: partner2Income,
        total: totalIncome,
      },
      expenses,
      netCashflow,
      cumulativeSavings,
    });
  }
  
  // Aggregate into yearly projections
  const yearlyProjections = aggregateYearlyProjections(monthlyProjections);
  
  // Calculate total cost
  const totalCost = yearlyProjections.reduce(
    (sum, year) => sum + year.totalExpenses,
    0
  );
  
  // Generate warnings
  const warnings = generateWarnings(monthlyProjections, profile, assumptions);
  
  return {
    profile,
    assumptions,
    monthlyProjections,
    yearlyProjections,
    totalCost,
    warnings,
    generatedAt: new Date().toISOString(),
  };
}

function calculateIncomeWithLeave(
  baseIncome: number,
  babyAgeMonths: number,
  leave: { durationWeeks: number; percentPaid: number }
): number {
  const leaveMonths = leave.durationWeeks / 4.33; // Convert weeks to months
  
  if (babyAgeMonths < leaveMonths) {
    // During leave period
    return baseIncome * (leave.percentPaid / 100);
  }
  
  return baseIncome;
}

function calculateMonthlyExpenses(
  babyAgeMonths: number,
  profile: UserFinancialProfile,
  assumptions: ExpenseAssumptions,
  costLevel: 'low' | 'average' | 'high'
): MonthlyProjection['expenses'] {
  const expenses = {
    housing: profile.monthlyHousingCost,
    childcare: 0,
    diapers: 0,
    food: 0,
    healthcare: 0,
    clothing: 0,
    oneTime: 0,
    miscellaneous: 0,
    total: 0,
  };
  
  // One-time costs (spread across first 3 months)
  if (babyAgeMonths === 0) {
    expenses.oneTime += assumptions.oneTimeCosts.crib;
    expenses.oneTime += assumptions.oneTimeCosts.carSeat;
    expenses.oneTime += assumptions.oneTimeCosts.babyMonitor;
  } else if (babyAgeMonths === 1) {
    expenses.oneTime += assumptions.oneTimeCosts.stroller;
    expenses.oneTime += assumptions.oneTimeCosts.changingTable;
  } else if (babyAgeMonths === 2) {
    expenses.oneTime += assumptions.oneTimeCosts.highChair;
  }
  
  // Get age-appropriate recurring costs from reference data
  const recurringCosts = getMonthlyRecurringCosts(babyAgeMonths, costLevel);
  
  // Map reference data categories to our expense structure
  expenses.diapers = recurringCosts['Diapers & Wipes'] || 0;
  expenses.food = recurringCosts['Formula & Food'] || 0;
  expenses.clothing = recurringCosts['Clothing'] || 0;
  expenses.healthcare = recurringCosts['Healthcare'] || 0;
  expenses.miscellaneous = (recurringCosts['Personal Care'] || 0) + 
                          (recurringCosts['Toys & Books'] || 0) + 
                          (recurringCosts['Miscellaneous'] || 0);
  
  // Childcare (starts at specified month)
  if (babyAgeMonths >= assumptions.childcareStartMonth) {
    if (profile.childcarePreference === 'daycare') {
      expenses.childcare = assumptions.childcareCosts.daycare;
    } else if (profile.childcarePreference === 'nanny') {
      expenses.childcare = assumptions.childcareCosts.nanny;
    }
    // stay-at-home has no direct cost
  }
  
  expenses.total =
    expenses.housing +
    expenses.childcare +
    expenses.diapers +
    expenses.food +
    expenses.healthcare +
    expenses.clothing +
    expenses.oneTime +
    expenses.miscellaneous;
  
  return expenses;
}

function aggregateYearlyProjections(
  monthlyProjections: MonthlyProjection[]
): YearlyProjection[] {
  const yearlyData: YearlyProjection[] = [];
  
  for (let year = 1; year <= 5; year++) {
    const yearMonths = monthlyProjections.filter((m) => m.year === year);
    
    const totalIncome = yearMonths.reduce((sum, m) => sum + m.income.total, 0);
    const totalExpenses = yearMonths.reduce((sum, m) => sum + m.expenses.total, 0);
    const netCashflow = totalIncome - totalExpenses;
    const endingSavings = yearMonths[yearMonths.length - 1].cumulativeSavings;
    
    const expenseBreakdown = {
      housing: yearMonths.reduce((sum, m) => sum + m.expenses.housing, 0),
      childcare: yearMonths.reduce((sum, m) => sum + m.expenses.childcare, 0),
      diapers: yearMonths.reduce((sum, m) => sum + m.expenses.diapers, 0),
      food: yearMonths.reduce((sum, m) => sum + m.expenses.food, 0),
      healthcare: yearMonths.reduce((sum, m) => sum + m.expenses.healthcare, 0),
      clothing: yearMonths.reduce((sum, m) => sum + m.expenses.clothing, 0),
      oneTime: yearMonths.reduce((sum, m) => sum + m.expenses.oneTime, 0),
      miscellaneous: yearMonths.reduce((sum, m) => sum + m.expenses.miscellaneous, 0),
    };
    
    yearlyData.push({
      year,
      totalIncome,
      totalExpenses,
      netCashflow,
      endingSavings,
      expenseBreakdown,
    });
  }
  
  return yearlyData;
}

function generateWarnings(
  monthlyProjections: MonthlyProjection[],
  profile: UserFinancialProfile,
  assumptions: ExpenseAssumptions
): Warning[] {
  const warnings: Warning[] = [];
  
  // Check for negative cashflow months
  const negativeCashflowMonths = monthlyProjections
    .filter((m) => m.netCashflow < 0)
    .map((m) => m.month);
  
  if (negativeCashflowMonths.length > 0) {
    warnings.push({
      severity: 'critical',
      title: 'Negative Cashflow Detected',
      message: `Your expenses exceed income in ${negativeCashflowMonths.length} month(s) over the 5-year period.`,
      monthsAffected: negativeCashflowMonths,
      recommendation:
        'Consider building an emergency fund before baby arrives, or explore ways to reduce expenses or increase income during these periods.',
    });
  }
  
  // Check for low savings buffer
  const minSavings = Math.min(...monthlyProjections.map((m) => m.cumulativeSavings));
  const recommendedBuffer = (profile.partner1Income + profile.partner2Income) * 3; // 3 months expenses
  
  if (minSavings < recommendedBuffer) {
    warnings.push({
      severity: 'important',
      title: 'Low Savings Buffer',
      message: `Your savings may drop below the recommended 3-month emergency fund (${formatCurrency(recommendedBuffer)}).`,
      recommendation:
        'Try to build up your emergency fund before baby arrives. Aim for at least 3-6 months of expenses.',
    });
  }
  
  // Check for high childcare costs
  const childcareCost =
    profile.childcarePreference === 'daycare'
      ? assumptions.childcareCosts.daycare
      : profile.childcarePreference === 'nanny'
      ? assumptions.childcareCosts.nanny
      : 0;
  
  const totalIncome = profile.partner1Income + profile.partner2Income;
  const childcarePercentage = (childcareCost / totalIncome) * 100;
  
  if (childcarePercentage > 30 && childcareCost > 0) {
    warnings.push({
      severity: 'important',
      title: 'High Childcare Costs',
      message: `Childcare represents ${childcarePercentage.toFixed(0)}% of your monthly income (${formatCurrency(childcareCost)}/month).`,
      recommendation:
        'Consider exploring alternative childcare options, flexible work arrangements, or whether one partner staying home might be financially comparable.',
    });
  }
  
  // Check parental leave impact
  const leaveMonths = Math.max(
    profile.partner1Leave.durationWeeks / 4.33,
    profile.partner2Leave.durationWeeks / 4.33
  );
  
  if (leaveMonths > 3 && (profile.partner1Leave.percentPaid < 100 || profile.partner2Leave.percentPaid < 100)) {
    warnings.push({
      severity: 'informational',
      title: 'Extended Parental Leave Period',
      message: `Your parental leave extends beyond 3 months with reduced pay.`,
      recommendation:
        'Plan ahead for the income reduction during this period. Consider building extra savings or adjusting discretionary spending.',
    });
  }
  
  return warnings;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}