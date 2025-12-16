---
title: Product Requirements Document
app: vigilant-tardigrade-twirl
created: 2025-12-14T18:28:51.860Z
version: 1
source: Deep Mode PRD Generation
---

# PRODUCT REQUIREMENTS DOCUMENT

## EXECUTIVE SUMMARY

**Product Vision:** NestWorth is an AI-powered financial planning tool that helps new and expecting parents understand the financial impact of having a baby by generating a comprehensive 5-year budget projection in under 5 minutes.

**Core Purpose:** Eliminates financial uncertainty for new parents by providing clear, personalized cost projections, cashflow warnings, and empathetic guidance based on their specific circumstances.

**Target Users:** New and expecting parents in the United States who want to understand and plan for the financial impact of having a baby.

**Key Features:**
- User Account Management (User-Generated Content)
- Financial Profile Onboarding (User-Generated Content)
- 5-Year Financial Projection Generation (System Data)
- AI-Powered Empathetic Summary (Communication)
- PDF Export of Financial Plans (User-Generated Content)

**Complexity Assessment:** Simple
- **State Management:** Local (single-user financial calculations)
- **External Integrations:** 1 (OpenAI API for summaries - reduces complexity)
- **Business Logic:** Moderate (deterministic financial calculations)
- **Data Synchronization:** None (calculations are stateless)

**MVP Success Metrics:**
- Users can complete onboarding and generate a 5-year projection in under 5 minutes
- All financial calculations produce accurate, deterministic results
- Users can download their financial plan as a PDF
- AI summaries accurately reflect calculated numbers without inventing data

## 1. USERS & PERSONAS

**Primary Persona:**
- **Name:** Sarah Chen
- **Context:** 32-year-old expecting her first child in 4 months, works full-time as a marketing manager, partner is a software engineer
- **Goals:** Understand total costs of having a baby, plan for childcare expenses, ensure they have adequate savings
- **Needs:** Clear financial projections, realistic cost estimates, understanding of when major expenses occur, reassurance about financial preparedness

**Secondary Persona:**
- **Name:** Marcus Johnson
- **Context:** 28-year-old new father with a 2-month-old, single income household while partner takes extended parental leave
- **Goals:** Understand cashflow impact during parental leave period, plan for return to dual income, budget for ongoing childcare
- **Needs:** Warning about cashflow gaps, understanding of childcare cost options, visibility into when financial pressure eases

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 User-Requested Features (All are Priority 0)

**FR-001: User Account Management**
- **Description:** Secure user registration and authentication system allowing users to create accounts, log in, and manage their profile information
- **Entity Type:** Configuration/System
- **User Benefit:** Protects user financial data and allows users to return to view their projections
- **Primary User:** All users
- **Lifecycle Operations:**
  - **Create:** Register new account with email, name, password
  - **View:** View profile information
  - **Edit:** Update name, email, password
  - **Delete:** Account deletion with data export option
  - **Additional:** Password reset, session management
- **Acceptance Criteria:**
  - [ ] Given valid email/name/password, when user registers, then account is created and user is logged in
  - [ ] Given existing account, when user logs in with correct credentials, then access is granted
  - [ ] Given incorrect credentials, when user attempts login, then clear error message is shown
  - [ ] Users can reset forgotten passwords via email
  - [ ] Users can update their profile information
  - [ ] Users can delete their account with confirmation

**FR-002: Financial Profile Onboarding (Complete Version)**
- **Description:** Guided onboarding form collecting essential financial and family planning information (≤10 questions) to generate personalized projections
- **Entity Type:** User-Generated Content
- **User Benefit:** Provides personalized financial projections based on their specific circumstances
- **Primary User:** All users (required before generating projections)
- **Lifecycle Operations:**
  - **Create:** Complete onboarding form with financial and family details
  - **View:** Review submitted profile information
  - **Edit:** Update any profile field to regenerate projections
  - **Delete:** Not allowed (archive only - needed for projection history)
  - **List/Search:** View all saved profiles (for future multi-child support)
  - **Additional:** Save as draft, validate inputs, show progress indicator
- **Acceptance Criteria:**
  - [ ] Given new user, when accessing app, then onboarding form is presented
  - [ ] Given onboarding form, when user enters all required fields, then form validates and allows submission
  - [ ] Given incomplete form, when user attempts to submit, then validation errors are clearly shown
  - [ ] Users can view their submitted profile information
  - [ ] Users can edit any profile field and regenerate projections
  - [ ] Profile data is preserved and associated with user account
  - [ ] Form completion takes under 3 minutes
  - [ ] Progress indicator shows completion status

**FR-003: 5-Year Financial Projection Generation**
- **Description:** Deterministic calculation engine that generates year-by-year cost projections, monthly cashflow analysis, and financial warnings based on user's profile and hardcoded expense assumptions
- **Entity Type:** System Data (generated from user profile)
- **User Benefit:** Provides clear visibility into expected costs and potential financial challenges over 5 years
- **Primary User:** All users
- **Lifecycle Operations:**
  - **Create:** Automatically generated when profile is submitted or updated
  - **View:** Display in results page with year-by-year breakdown
  - **Edit:** Not allowed (regenerate by editing profile)
  - **Delete:** Not allowed (archive only - maintains calculation history)
  - **List/Search:** View projection history (for tracking changes over time)
  - **Additional:** Export to PDF, compare scenarios (deferred)
- **Acceptance Criteria:**
  - [ ] Given complete profile, when user submits, then 5-year projection is generated in under 5 seconds
  - [ ] Given same inputs, when projection is generated multiple times, then identical results are produced (deterministic)
  - [ ] Projection includes year-by-year cost breakdown for all expense categories
  - [ ] Projection includes monthly cashflow analysis showing income vs expenses
  - [ ] One-time costs (crib, stroller, car seat, high chair) appear in appropriate months
  - [ ] Recurring costs (diapers, clothes, food, childcare) are calculated monthly
  - [ ] Childcare costs begin at month 6 or based on user's preference (daycare/nanny/stay-at-home)
  - [ ] Parental leave impact on income is accurately reflected
  - [ ] Regional childcare cost band is based on reference data provided by ZIP code (low/med/high), if Zipcode not available assume med by default
  - [ ] Assumptions used are visible and explained to user

**FR-004: Financial Warning System**
- **Description:** Automated analysis of projection data to identify and highlight potential financial challenges, cashflow gaps, and periods of high expense
- **Entity Type:** System Data (derived from projection)
- **User Benefit:** Proactive awareness of financial pressure points allows better planning and preparation
- **Primary User:** All users
- **Lifecycle Operations:**
  - **Create:** Automatically generated with projection
  - **View:** Display as callout boxes on results page
  - **Edit:** Not allowed (regenerate by editing profile)
  - **Delete:** Not allowed (part of projection record)
  - **Additional:** Prioritize warnings by severity
- **Acceptance Criteria:**
  - [ ] Given projection with negative cashflow months, when warnings are generated, then cashflow warnings are displayed
  - [ ] Given projection with savings below recommended buffer, when warnings are generated, then savings warnings are displayed
  - [ ] Given projection with high childcare costs, when warnings are generated, then cost warnings are displayed
  - [ ] Warnings are prioritized by severity (critical/important/informational)
  - [ ] Each warning includes specific month/year and recommended action
  - [ ] Warnings are visually distinct and easy to identify on results page

**FR-005: AI-Powered Empathetic Summary**
- **Description:** LLM-generated narrative summary that explains the financial projection in empathetic, accessible language, strictly using only the calculated numbers without inventing data
- **Entity Type:** Communication
- **User Benefit:** Makes complex financial data understandable and provides emotional support during financial planning
- **Primary User:** All users
- **Lifecycle Operations:**
  - **Create:** Generated after projection calculation completes
  - **View:** Display on results page and in PDF export
  - **Edit:** Regenerate with same projection data (for tone/clarity improvements)
  - **Delete:** Not allowed (preserved with projection)
  - **Additional:** Version history for regenerations
- **Acceptance Criteria:**
  - [ ] Given completed projection, when AI summary is generated, then summary references only calculated numbers
  - [ ] Given projection data, when AI summary is generated, then summary is empathetic and supportive in tone
  - [ ] Given projection warnings, when AI summary is generated, then warnings are explained with context and actionable advice
  - [ ] AI summary does not invent or estimate any financial figures
  - [ ] AI summary includes disclaimer: "This summary is based on your specific inputs and general assumptions. Not financial advice."
  - [ ] Summary is generated in under 10 seconds
  - [ ] Summary is readable at 8th-grade level
  - [ ] Summary highlights key insights (total 5-year cost, highest expense periods, savings recommendations)

**FR-006: PDF Export of Financial Plans**
- **Description:** Downloadable PDF document containing the complete financial projection, year-by-year breakdown, warnings, AI summary, and assumptions used
- **Entity Type:** User-Generated Content (export of system data)
- **User Benefit:** Allows users to save, print, and share their financial plan with partners or advisors
- **Primary User:** All users
- **Lifecycle Operations:**
  - **Create:** Generate PDF on-demand from results page
  - **View:** Preview before download (optional for MVP)
  - **Edit:** Not applicable (regenerate by updating profile)
  - **Delete:** User manages downloaded files locally
  - **List/Search:** Download history (deferred)
  - **Additional:** Email PDF to user (deferred)
- **Acceptance Criteria:**
  - [ ] Given results page, when user clicks "Download PDF", then PDF is generated and downloaded
  - [ ] PDF includes complete year-by-year financial breakdown
  - [ ] PDF includes all warning callouts
  - [ ] PDF includes AI summary
  - [ ] PDF includes assumptions and disclaimers
  - [ ] PDF includes user's profile inputs (for reference)
  - [ ] PDF has basic professional layout (readable, organized)
  - [ ] PDF generation completes in under 5 seconds
  - [ ] PDF filename includes user name and generation date

### 2.2 Essential Market Features

**FR-007: Assumption Transparency**
- **Description:** Clear display of all hardcoded assumptions used in calculations, including cost bands, regional adjustments, and timing assumptions
- **Entity Type:** System Data
- **User Benefit:** Builds trust by showing exactly how projections are calculated
- **Primary User:** All users
- **Lifecycle Operations:**
  - **View:** Display assumptions on results page and in PDF
  - **Additional:** Link to detailed assumption methodology
- **Acceptance Criteria:**
  - [ ] All hardcoded cost assumptions are visible to users
  - [ ] Regional cost band (low/med/high) is shown with explanation
  - [ ] Timing assumptions (e.g., "daycare starts at month 6") are clearly stated
  - [ ] Users can access detailed assumption methodology
  - [ ] Assumptions are included in PDF export

**FR-008: Legal Disclaimers**
- **Description:** Required legal disclaimers stating that projections are estimates and not financial advice
- **Entity Type:** System/Configuration
- **User Benefit:** Sets appropriate expectations and protects both user and company
- **Primary User:** All users
- **Lifecycle Operations:**
  - **View:** Display on results page, in AI summary, and in PDF
- **Acceptance Criteria:**
  - [ ] Disclaimer appears on results page: "These projections are estimates based on general assumptions and your inputs. This is not financial advice. Consult a financial advisor for personalized guidance."
  - [ ] Disclaimer is included in AI summary
  - [ ] Disclaimer is included in PDF export
  - [ ] Disclaimer is clearly visible and readable

## 3. USER WORKFLOWS

### 3.1 Primary Workflow: Generate First Financial Projection

**Trigger:** New user wants to understand baby costs
**Outcome:** User receives complete 5-year financial projection with AI summary and can download PDF

**Steps:**
1. User navigates to NestWorth landing page
2. User clicks "Get Started" or "Create Account"
3. System displays registration form (email, name, password)
4. User completes registration and submits
5. System creates account and logs user in
6. System displays onboarding form with progress indicator
7. User enters financial profile information:
   - Partner 1 Monthly Take home income after tax and Insurance
   - Partner 2 Monthly Take home income after tax and Insurance
   - ZIP code
   - Due date / Baby's birth date
   - Current savings
   - Childcare preference (daycare/nanny/stay-at-home)
   - Partner 1 parental leave (duration + % paid)
   - Partner 2 parental leave (duration + % paid)
   - Average monthly housing costs ( Rent/Mortgage)

8. System validates inputs in real-time
9. User clicks "Generate My Plan"
10. System displays loading state ("Calculating your 5-year projection...")
11. System executes deterministic calculation engine:
    - Retrieves hardcoded expense assumptions based on profile
    - Calculates year-by-year projections
    - Generates cashflow warnings
12. System calls OpenAI API to generate empathetic summary using only calculated numbers
13. System displays results page with:
    - 5-year total cost summary
    - Year-by-year breakdown table
    - Warning callouts (if any)
    - AI empathetic summary
    - Assumptions used
    - Disclaimers
14. User reviews projection and summary
15. User clicks "Download PDF"
16. System generates PDF with all projection data
17. User receives PDF download
18. Workflow complete (under 5 minutes total)

**Alternative Paths:**
- If validation fails at step 8, system shows specific field errors and user corrects
- If AI summary generation fails at step 12, system shows projection without summary and offers retry
- If PDF generation fails at step 16, system shows error and offers retry

### 3.2 Entity Management Workflows

**Financial Profile Management Workflow**

**Create Profile:**
1. User completes registration (if new user)
2. System displays onboarding form
3. User fills in all required fields (≤10 questions)
4. System validates inputs in real-time
5. User clicks "Generate My Plan"
6. System saves profile and generates projection

**View Profile:**
1. User navigates to "My Profile" or "Edit Inputs"
2. System displays current profile information
3. User can review all submitted data

**Edit Profile:**
1. User clicks "Edit Inputs" from results page or navigation
2. System displays onboarding form pre-filled with current data
3. User modifies any field(s)
4. System validates changes
5. User clicks "Update & Regenerate"
6. System saves updated profile and regenerates projection
7. System displays updated results page

**View Projection:**
1. User logs into account
2. System displays most recent projection on dashboard
3. User can view year-by-year breakdown
4. User can view warnings and AI summary
5. User can view assumptions used

**Download PDF:**
1. User navigates to results page
2. User clicks "Download PDF" button
3. System generates PDF with current projection data
4. System initiates download
5. User receives PDF file

**Account Management Workflow**

**Create Account:**
1. User navigates to registration page
2. User enters email, name, password
3. System validates inputs (email format, password strength)
4. User submits registration
5. System creates account and logs user in

**Login:**
1. User navigates to login page
2. User enters email and password
3. System validates credentials
4. If valid, system logs user in and redirects to dashboard
5. If invalid, system shows error message

**Edit Account:**
1. User navigates to account settings
2. User clicks "Edit Profile"
3. User modifies name, email, or password
4. System validates changes
5. User saves changes
6. System confirms update

**Delete Account:**
1. User navigates to account settings
2. User clicks "Delete Account"
3. System displays confirmation dialog with warning
4. User confirms deletion
5. System offers data export option
6. System deletes account and all associated data
7. System logs user out

### 3.3 Calculation Engine Workflow

**Trigger:** User submits or updates financial profile
**Outcome:** Complete 5-year projection with warnings

**Steps:**
1. System receives UserFinancialProfile data
2. System calls `getBabyExpenseAssumptions(profile)`:
   - Retrive childcare cost band based on ZIP code (low/med/high)
   - Retrieves hardcoded one-time costs (crib, stroller, car seat, etc.)
   - Retrieves hardcoded monthly recurring costs (diapers, food, etc.)