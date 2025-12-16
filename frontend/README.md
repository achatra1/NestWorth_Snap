# NestWorth - Baby Budget Blueprint

An AI-powered financial planning tool that helps new and expecting parents understand the financial impact of having a baby by generating a comprehensive 5-year budget projection.

## Features

- **User Authentication**: Secure registration and login (frontend-only using localStorage)
- **Financial Profile Onboarding**: Guided 10-question form to collect essential information
- **5-Year Financial Projection**: Deterministic calculation engine with year-by-year breakdown
- **Warning System**: Automated detection of cashflow issues and financial challenges
- **AI-Powered Summary**: Empathetic, template-based summary of financial projections
- **PDF Export**: Download complete financial plan using browser print functionality
- **Assumption Transparency**: Clear display of all assumptions used
- **Reference Data Tables**: Real cost data from national surveys and regional childcare databases

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **Routing**: React Router v6
- **State Management**: React Context API
- **Data Persistence**: localStorage (frontend-only)
- **PDF Export**: Browser print functionality

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to `http://localhost:5137`

## Usage

1. **Register**: Create a new account with email, name, and password
2. **Onboarding**: Complete the 3-step financial profile form (≤10 questions)
3. **View Results**: See your 5-year projection with year-by-year breakdown
4. **Review Warnings**: Check for any financial challenges or cashflow issues
5. **Read AI Summary**: Get an empathetic explanation of your financial situation
6. **Download PDF**: Export your complete financial plan
7. **Edit Inputs**: Update your profile to regenerate projections

## Project Structure

```
src/
├── components/        # Reusable UI components (shadcn/ui)
├── contexts/          # React contexts (AuthContext)
├── data/             # Reference data tables
│   ├── childcareCostsByZip.ts    # Weekly childcare costs by ZIP
│   ├── oneTimeCosts.ts           # One-time baby expenses
│   └── recurringCosts.ts         # Monthly recurring expenses
├── pages/            # Page components
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Onboarding.tsx
│   └── Results.tsx
├── types/            # TypeScript interfaces
│   └── financial.ts
├── utils/            # Utility functions
│   ├── expenseAssumptions.ts    # Cost calculation logic
│   ├── projectionCalculator.ts  # Calculation engine
│   └── aiSummaryGenerator.ts    # Template-based summaries
└── App.tsx           # Main app component with routing
```

## Reference Data Tables

The application uses three reference data tables for accurate cost calculations:

### 1. Childcare Costs by ZIP Code
**File**: `src/data/childcareCostsByZip.ts`

Contains weekly childcare costs by ZIP code, including:
- Infant care costs (0-12 months)
- Toddler care costs (12-36 months)
- Preschool care costs (3-5 years)
- State and city information

**Data Source**: National childcare cost surveys and regional databases

**Usage**: 
- Automatically looks up costs based on user's ZIP code
- Falls back to national averages if ZIP not found
- Converts weekly costs to monthly (multiply by 4.33)

### 2. One-Time Expenses
**File**: `src/data/oneTimeCosts.ts`

Contains one-time baby expenses with low/average/high cost ranges:
- **Nursery Furniture**: Crib, mattress, changing table, dresser, glider
- **Transportation**: Car seat, stroller, baby carrier
- **Feeding**: High chair, bottles, breast pump
- **Safety**: Baby monitor, gates
- **Bathing**: Baby bathtub
- **Other**: Diaper bag, play mat, swing/bouncer

**Cost Levels**:
- **Low**: Budget-friendly options
- **Average**: Mid-range quality
- **High**: Premium brands

### 3. Recurring Monthly Expenses
**File**: `src/data/recurringCosts.ts`

Contains age-based monthly expenses with low/average/high ranges:
- **Diapers & Wipes**: Decreases after potty training (~30 months)
- **Formula & Food**: Formula (0-12 months), baby food (6-12 months), toddler food (12+ months)
- **Clothing**: Size-based costs that increase with age
- **Healthcare**: Co-pays, medications, dental care
- **Personal Care**: Bath products, extra laundry
- **Toys & Books**: Age-appropriate items
- **Miscellaneous**: Unexpected expenses

**Age-Based Logic**:
- Each expense has a `startMonth` (when it begins)
- Optional `endMonth` (when it stops, e.g., formula at 12 months)
- Costs automatically adjust as baby grows

## Calculation Engine

The projection calculator is **deterministic** - same inputs always produce identical results.

### Core Functions

1. **`getBabyExpenseAssumptions(profile)`**
   - Looks up childcare costs by ZIP code from reference data
   - Determines cost band (low/medium/high) based on regional childcare costs
   - Retrieves one-time costs from reference table
   - Gets age-appropriate recurring costs from reference table
   - Returns complete expense assumptions

2. **`calculateFiveYearProjection(profile)`**
   - Generates 60 monthly projections (5 years)
   - Accounts for parental leave income reduction
   - Calculates age-based expenses using reference data
   - Tracks cumulative savings
   - Aggregates into yearly summaries

3. **`generateWarnings(projection)`**
   - Detects negative cashflow months
   - Identifies low savings buffer
   - Flags high childcare costs (>30% of income)
   - Provides actionable recommendations

4. **`generateAISummary(projection)`**
   - Creates empathetic narrative using calculated data
   - **Does not invent any numbers**
   - Highlights key insights and warnings
   - Includes legal disclaimers

### Cost Band Determination

The system automatically determines cost level based on childcare costs:
- **Low**: Weekly infant care < $280
- **Medium**: Weekly infant care $280-$400
- **High**: Weekly infant care > $400

This cost band is then applied to one-time and recurring expenses.

## Example Cost Calculations

### High-Cost Area (NYC, ZIP 10001)
- Weekly infant daycare: $450 → Monthly: $1,949
- One-time costs: High range (e.g., crib $800)
- Recurring costs: High range (e.g., diapers $120/mo)

### Medium-Cost Area (Chicago, ZIP 60601)
- Weekly infant daycare: $350 → Monthly: $1,516
- One-time costs: Average range (e.g., crib $300)
- Recurring costs: Average range (e.g., diapers $80/mo)

### Low-Cost Area (Birmingham, ZIP 35004)
- Weekly infant daycare: $240 → Monthly: $1,039
- One-time costs: Low range (e.g., crib $150)
- Recurring costs: Low range (e.g., diapers $60/mo)

## Age-Based Cost Changes

The calculator automatically adjusts costs as baby grows:

**Month 0-6**: Formula, diapers, newborn clothes, basic healthcare
**Month 6-12**: Add baby food, reduce formula, childcare starts
**Month 12-24**: Stop formula, increase food costs, toddler clothes
**Month 24-36**: Potty training (reduce diapers), preschool clothes
**Month 36-60**: No diapers, increased food/clothing, preschool activities

## Future Enhancements

The codebase is structured to easily add:

1. **Expanded Reference Data**
   - More comprehensive ZIP code coverage
   - Regional price variations for all categories
   - Seasonal cost adjustments

2. **Scenario Modeling**
   - Compare different childcare options
   - Model income changes
   - Test different savings strategies

3. **Tax Planning**
   - Child Tax Credit calculations
   - Dependent Care FSA optimization
   - State-specific tax benefits

4. **Healthcare Costs**
   - Insurance premium changes
   - Deductible tracking
   - HSA/FSA planning

5. **Real Backend Integration**
   - Replace localStorage with database
   - User data persistence
   - Historical tracking

6. **Real AI Integration**
   - Connect to OpenAI API
   - Dynamic, personalized summaries
   - Conversational Q&A

7. **Multi-Child Support**
   - Track multiple children
   - Sibling cost adjustments
   - Family planning scenarios

8. **Expense Tracking**
   - Compare actual vs projected
   - Budget variance analysis
   - Spending insights

## Data Models

### UserFinancialProfile
```typescript
{
  userId: string;
  partner1Income: number;
  partner2Income: number;
  zipCode: string;
  dueDate: string;
  currentSavings: number;
  childcarePreference: 'daycare' | 'nanny' | 'stay-at-home';
  partner1Leave: { durationWeeks: number; percentPaid: number };
  partner2Leave: { durationWeeks: number; percentPaid: number };
  monthlyHousingCost: number;
}
```

### FiveYearProjection
```typescript
{
  profile: UserFinancialProfile;
  assumptions: ExpenseAssumptions;
  monthlyProjections: MonthlyProjection[];
  yearlyProjections: YearlyProjection[];
  totalCost: number;
  warnings: Warning[];
  generatedAt: string;
}
```

## Important Notes

- **Frontend-Only**: All data stored in localStorage (not production-ready)
- **No Real Authentication**: Passwords stored in plain text (demo only)
- **Template-Based AI**: Summary uses templates, not real LLM
- **Reference Data**: Based on national surveys and regional databases
- **Cost Variations**: Actual costs vary by location, choices, and circumstances
- **Not Financial Advice**: Always includes disclaimers

## Updating Reference Data

To update the reference data tables:

1. **Childcare Costs**: Edit `src/data/childcareCostsByZip.ts`
   - Add new ZIP codes with weekly costs
   - Update existing costs based on new surveys

2. **One-Time Costs**: Edit `src/data/oneTimeCosts.ts`
   - Add new items or categories
   - Update price ranges based on market research

3. **Recurring Costs**: Edit `src/data/recurringCosts.ts`
   - Add new expense categories
   - Adjust age ranges and costs
   - Update start/end months for expenses

The calculation engine will automatically use the updated data.

## License

MIT

## Contributing

Contributions welcome for:
- More comprehensive ZIP code database
- Updated cost data from recent surveys
- Additional expense categories
- Improved cost calculation logic
- Real backend integration
- Enhanced PDF export styling