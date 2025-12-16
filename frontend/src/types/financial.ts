export interface UserFinancialProfile {
  userId: string;
  partner1Income: number; // Monthly take-home
  partner2Income: number; // Monthly take-home
  zipCode: string;
  dueDate: string; // ISO date string
  currentSavings: number;
  childcarePreference: 'daycare' | 'nanny' | 'stay-at-home';
  partner1Leave: {
    durationWeeks: number;
    percentPaid: number; // 0-100
  };
  partner2Leave: {
    durationWeeks: number;
    percentPaid: number; // 0-100
  };
  monthlyHousingCost: number;
}

export interface ExpenseAssumptions {
  costBand: 'low' | 'medium' | 'high';
  oneTimeCosts: {
    crib: number;
    stroller: number;
    carSeat: number;
    highChair: number;
    babyMonitor: number;
    changingTable: number;
  };
  monthlyRecurring: {
    diapers: number;
    wipes: number;
    formula: number; // Assuming formula feeding
    babyFood: number; // Starts around month 6
    clothing: number;
    healthcare: number; // Co-pays, medications
    miscellaneous: number;
  };
  childcareCosts: {
    daycare: number; // Monthly
    nanny: number; // Monthly
    stayAtHome: number; // Opportunity cost (0 for MVP)
  };
  childcareStartMonth: number; // Default 6
}

export interface MonthlyProjection {
  month: number; // 1-60 (5 years)
  year: number; // 1-5
  monthOfYear: number; // 1-12
  income: {
    partner1: number;
    partner2: number;
    total: number;
  };
  expenses: {
    housing: number;
    childcare: number;
    diapers: number;
    food: number;
    healthcare: number;
    clothing: number;
    oneTime: number;
    miscellaneous: number;
    total: number;
  };
  netCashflow: number;
  cumulativeSavings: number;
}

export interface YearlyProjection {
  year: number;
  totalIncome: number;
  totalExpenses: number;
  netCashflow: number;
  endingSavings: number;
  expenseBreakdown: {
    housing: number;
    childcare: number;
    diapers: number;
    food: number;
    healthcare: number;
    clothing: number;
    oneTime: number;
    miscellaneous: number;
  };
}

export interface FiveYearProjection {
  profile: UserFinancialProfile;
  assumptions: ExpenseAssumptions;
  monthlyProjections: MonthlyProjection[];
  yearlyProjections: YearlyProjection[];
  totalCost: number;
  warnings: Warning[];
  generatedAt: string;
}

export interface Warning {
  severity: 'critical' | 'important' | 'informational';
  title: string;
  message: string;
  monthsAffected?: number[];
  recommendation: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}