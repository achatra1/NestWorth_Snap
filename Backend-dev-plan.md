# Backend Development Plan - NestWorth

## 1️⃣ Executive Summary

**What Will Be Built:**
- FastAPI backend for NestWorth baby budget calculator
- User authentication with JWT tokens
- Financial profile management with MongoDB Atlas storage
- 5-year projection calculation engine
- AI-powered summary generation via OpenAI API
- PDF export functionality

**Why:**
- Replace frontend localStorage with persistent database storage
- Enable secure multi-device access to user data
- Provide scalable backend for future features

**Constraints:**
- FastAPI with Python 3.13 (async)
- MongoDB Atlas using Motor and Pydantic v2
- No Docker deployment
- Manual testing after every task via frontend UI
- Single Git branch `main` only
- API base path `/api/v1/*`

**Sprint Structure:**
- **S0:** Environment setup and health check
- **S1:** User authentication (signup/login/logout)
- **S2:** Financial profile management
- **S3:** Projection calculation and warnings
- **S4:** AI summary generation
- **S5:** PDF export

---

## 2️⃣ In-Scope & Success Criteria

**In-Scope Features:**
- User registration and authentication
- Secure session management with JWT
- Financial profile CRUD operations
- 5-year projection calculation with warnings
- AI-powered empathetic summaries
- PDF generation and download
- Regional childcare cost lookup by ZIP code

**Success Criteria:**
- All frontend features work end-to-end with backend
- User data persists across sessions and devices
- All task-level manual tests pass via UI
- Projections match frontend calculation logic exactly
- Each sprint's code pushed to `main` after verification

---

## 3️⃣ API Design

**Base Path:** `/api/v1`

**Error Envelope:** `{ "error": "message" }`

### Health Check
- **GET** `/healthz`
- **Purpose:** Verify backend and database connectivity
- **Response:** `{ "status": "ok", "database": "connected", "timestamp": "ISO-8601" }`

### Authentication Endpoints

- **POST** `/api/v1/auth/signup`
- **Purpose:** Register new user account
- **Request:** `{ "email": "string", "name": "string", "password": "string" }`
- **Response:** `{ "user": { "id": "string", "email": "string", "name": "string" }, "token": "jwt-string" }`
- **Validation:** Email format, password min 8 chars, unique email

- **POST** `/api/v1/auth/login`
- **Purpose:** Authenticate existing user
- **Request:** `{ "email": "string", "password": "string" }`
- **Response:** `{ "user": { "id": "string", "email": "string", "name": "string" }, "token": "jwt-string" }`
- **Validation:** Credentials match, account exists

- **POST** `/api/v1/auth/logout`
- **Purpose:** Invalidate user session (client-side token removal)
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `{ "message": "Logged out successfully" }`

- **GET** `/api/v1/auth/me`
- **Purpose:** Get current user info from token
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `{ "id": "string", "email": "string", "name": "string" }`

### Profile Endpoints

- **POST** `/api/v1/profiles`
- **Purpose:** Create or update user's financial profile
- **Headers:** `Authorization: Bearer <token>`
- **Request:** `{ "partner1Income": number, "partner2Income": number, "zipCode": "string", "dueDate": "ISO-date", "currentSavings": number, "childcarePreference": "daycare|nanny|stay-at-home", "partner1Leave": { "durationWeeks": number, "percentPaid": number }, "partner2Leave": { "durationWeeks": number, "percentPaid": number }, "monthlyHousingCost": number }`
- **Response:** `{ "id": "string", "userId": "string", ...profile fields, "createdAt": "ISO-8601", "updatedAt": "ISO-8601" }`
- **Validation:** All numeric fields >= 0, zipCode 5 digits, childcarePreference enum

- **GET** `/api/v1/profiles/me`
- **Purpose:** Get current user's profile
- **Headers:** `Authorization: Bearer <token>`
- **Response:** Profile object or `{ "error": "Profile not found" }` if none exists

### Projection Endpoints

- **POST** `/api/v1/projections/calculate`
- **Purpose:** Generate 5-year projection from profile
- **Headers:** `Authorization: Bearer <token>`
- **Request:** `{ "profileId": "string" }` (optional, defaults to user's current profile)
- **Response:** `{ "profile": {...}, "assumptions": {...}, "monthlyProjections": [...], "yearlyProjections": [...], "totalCost": number, "warnings": [...], "generatedAt": "ISO-8601" }`
- **Validation:** Profile exists and belongs to user

### AI Summary Endpoints

- **POST** `/api/v1/summaries/generate`
- **Purpose:** Generate AI summary from projection data
- **Headers:** `Authorization: Bearer <token>`
- **Request:** `{ "projection": {...} }` (full projection object)
- **Response:** `{ "summary": "markdown-string", "generatedAt": "ISO-8601" }`
- **Validation:** Projection data complete

### PDF Export Endpoints

- **POST** `/api/v1/exports/pdf`
- **Purpose:** Generate PDF from projection and summary
- **Headers:** `Authorization: Bearer <token>`
- **Request:** `{ "projection": {...}, "summary": "string" }`
- **Response:** Binary PDF file with headers `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="nestworth-plan-{date}.pdf"`
- **Validation:** Projection and summary present

---

## 4️⃣ Data Model (MongoDB Atlas)

### Collection: `users`
**Fields:**
- `_id`: ObjectId (auto)
- `email`: string (required, unique, indexed)
- `name`: string (required)
- `password_hash`: string (required, Argon2)
- `created_at`: datetime (required, default now)
- `updated_at`: datetime (required, default now)

**Example:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "email": "sarah@example.com",
  "name": "Sarah Chen",
  "password_hash": "$argon2id$v=19$m=65536...",
  "created_at": "2025-12-15T10:00:00Z",
  "updated_at": "2025-12-15T10:00:00Z"
}
```

### Collection: `profiles`
**Fields:**
- `_id`: ObjectId (auto)
- `user_id`: ObjectId (required, indexed, ref users)
- `partner1_income`: float (required)
- `partner2_income`: float (required)
- `zip_code`: string (required, 5 chars)
- `due_date`: date (required)
- `current_savings`: float (required)
- `childcare_preference`: string (required, enum: daycare/nanny/stay-at-home)
- `partner1_leave`: object (required)
  - `duration_weeks`: int
  - `percent_paid`: int
- `partner2_leave`: object (required)
  - `duration_weeks`: int
  - `percent_paid`: int
- `monthly_housing_cost`: float (required)
- `created_at`: datetime (required, default now)
- `updated_at`: datetime (required, default now)

**Example:**
```json
{
  "_id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "partner1_income": 5000.0,
  "partner2_income": 4500.0,
  "zip_code": "10001",
  "due_date": "2026-04-15",
  "current_savings": 10000.0,
  "childcare_preference": "daycare",
  "partner1_leave": { "duration_weeks": 12, "percent_paid": 100 },
  "partner2_leave": { "duration_weeks": 12, "percent_paid": 60 },
  "monthly_housing_cost": 2000.0,
  "created_at": "2025-12-15T10:05:00Z",
  "updated_at": "2025-12-15T10:05:00Z"
}
```

---

## 5️⃣ Frontend Audit & Feature Map

### `/` (Login Page)
- **Purpose:** User authentication entry point
- **Data Needed:** None initially
- **Backend:** `POST /api/v1/auth/login`
- **Auth:** None (public)

### `/register` (Registration Page)
- **Purpose:** New user account creation
- **Data Needed:** None initially
- **Backend:** `POST /api/v1/auth/signup`
- **Auth:** None (public)

### `/onboarding` (Financial Profile Form)
- **Purpose:** Collect user financial data (3-step form)
- **Data Needed:** Existing profile if editing
- **Backend:** `GET /api/v1/profiles/me`, `POST /api/v1/profiles`
- **Auth:** Required (JWT)

### `/results` (Projection Results)
- **Purpose:** Display 5-year projection, warnings, AI summary
- **Data Needed:** Profile, projection, AI summary
- **Backend:** `GET /api/v1/profiles/me`, `POST /api/v1/projections/calculate`, `POST /api/v1/summaries/generate`
- **Auth:** Required (JWT)
- **Notes:** PDF download via `POST /api/v1/exports/pdf`

---

## 6️⃣ Configuration & ENV Vars

**Required Environment Variables:**
- `APP_ENV` — `development` or `production`
- `PORT` — HTTP port (default: `8000`)
- `MONGODB_URI` — MongoDB Atlas connection string (e.g., `mongodb+srv://user:pass@cluster.mongodb.net/nestworth`)
- `JWT_SECRET` — Secret key for JWT signing (min 32 chars)
- `JWT_EXPIRES_IN` — JWT expiration in seconds (default: `86400` = 24 hours)
- `CORS_ORIGINS` — Comma-separated allowed origins (e.g., `http://localhost:5173,https://app.nestworth.com`)
- `OPENAI_API_KEY` — OpenAI API key for summary generation

---

## 7️⃣ Background Work

**Not Required:** All operations are synchronous and complete within request lifecycle. No background tasks, queues, or async processing needed.

---

## 8️⃣ Integrations

### OpenAI API Integration
- **Purpose:** Generate empathetic AI summaries from projection data
- **Trigger:** User views results page
- **Flow:**
  1. Frontend requests projection calculation
  2. Backend calculates projection
  3. Backend calls OpenAI API with projection data
  4. Backend returns summary to frontend
- **Env Var:** `OPENAI_API_KEY`
- **Model:** `gpt-4o-mini` or `gpt-3.5-turbo`
- **Prompt:** Structured prompt with projection data, instructions to use only calculated numbers

---

## 9️⃣ Testing Strategy (Manual via Frontend)

**Validation Approach:**
- Every task includes manual test via frontend UI
- Test after each task completion (not only after sprints)
- If test fails, fix immediately before proceeding
- After all sprint tasks pass, commit and push to `main`

**Manual Test Format:**
- **Manual Test Step:** Exact UI action + expected result
- **User Test Prompt:** Copy-paste instruction for testing

---

## 🔟 Sprint Plan & Backlog

---

## 🧱 S0 – Environment Setup & Frontend Connection

**Objectives:**
- Create FastAPI skeleton with `/api/v1` base path and `/healthz`
- Connect to MongoDB Atlas using `MONGODB_URI`
- `/healthz` performs DB ping and returns JSON status
- Enable CORS for frontend origin
- Replace dummy API URLs in frontend with real backend URLs
- Initialize Git at root, set default branch to `main`, push to GitHub
- Create single `.gitignore` at root

**User Stories:**
- As a developer, I need a working backend skeleton so I can build features
- As a developer, I need database connectivity verified so I can store data
- As a frontend, I need CORS enabled so I can make API calls

**Tasks:**

1. **Initialize FastAPI project structure**
   - Create `backend/` directory at project root
   - Create `backend/main.py` with FastAPI app
   - Create `backend/requirements.txt` with dependencies: `fastapi`, `uvicorn[standard]`, `motor`, `pydantic`, `pydantic-settings`, `python-dotenv`, `argon2-cffi`, `pyjwt`, `python-multipart`, `openai`, `reportlab`
   - Create `backend/.env.example` with all required env vars
   - Create `backend/config.py` for settings management using Pydantic BaseSettings
   - **Manual Test Step:** Run `pip install -r requirements.txt` → all packages install successfully
   - **User Test Prompt:** "Install backend dependencies and confirm no errors."

2. **Implement `/healthz` endpoint with MongoDB ping**
   - Create `backend/database.py` with Motor async MongoDB client
   - Implement connection to MongoDB Atlas using `MONGODB_URI`
   - Create `/healthz` endpoint that pings database
   - Return `{ "status": "ok", "database": "connected", "timestamp": "ISO-8601" }`
   - **Manual Test Step:** Start backend, curl `/healthz` → 200 OK with DB status
   - **User Test Prompt:** "Start the backend with `uvicorn backend.main:app --reload` and visit http://localhost:8000/healthz. Confirm JSON shows database connected."

3. **Configure CORS for frontend**
   - Add CORS middleware to FastAPI app
   - Use `CORS_ORIGINS` from env (default: `http://localhost:5173`)
   - Allow credentials, all methods, all headers
   - **Manual Test Step:** Start backend and frontend, open browser console → no CORS errors
   - **User Test Prompt:** "Start both backend and frontend. Open browser DevTools Network tab and confirm no CORS errors when loading the app."

4. **Initialize Git repository and push to GitHub**
   - Run `git init` at project root (if not already initialized)
   - Create `.gitignore` at root with: `__pycache__/`, `*.pyc`, `.env`, `*.pyo`, `*.pyd`, `.Python`, `venv/`, `env/`, `.vscode/`, `.idea/`, `*.log`
   - Set default branch to `main`: `git branch -M main`
   - Create initial commit with backend skeleton
   - Create GitHub repository and push
   - **Manual Test Step:** Check GitHub → repository exists with backend code
   - **User Test Prompt:** "Visit your GitHub repository and confirm the backend code is present on the main branch."

**Definition of Done:**
- Backend runs locally on port 8000
- `/healthz` returns 200 OK with MongoDB connection status
- Frontend can make requests without CORS errors
- Code pushed to GitHub `main` branch
- `.gitignore` prevents sensitive files from being committed

**Post-Sprint:**
- Commit all changes with message: "S0: Environment setup complete"
- Push to `main` branch

---

## 🧩 S1 – Basic Auth (Signup / Login / Logout)

**Objectives:**
- Implement JWT-based signup, login, and logout
- Store users in MongoDB with Argon2 password hashing
- Protect one backend route and one frontend page

**User Stories:**
- As a new user, I can create an account so I can save my data
- As a returning user, I can log in so I can access my saved data
- As a logged-in user, I can log out so my session ends

**Endpoints:**
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

**Tasks:**

1. **Create User Pydantic model and MongoDB schema**
   - Create `backend/models/user.py` with Pydantic v2 model
   - Fields: `id`, `email`, `name`, `password_hash`, `created_at`, `updated_at`
   - Add email validation and unique constraint
   - **Manual Test Step:** Import model in Python shell → no errors
   - **User Test Prompt:** "Run `python -c 'from backend.models.user import User; print(User)'` and confirm no import errors."

2. **Implement signup endpoint with Argon2 hashing**
   - Create `backend/routers/auth.py` with signup route
   - Validate email format and password length (min 8 chars)
   - Check if email already exists in database
   - Hash password using `argon2-cffi`
   - Insert user into `users` collection
   - Generate JWT token with user ID
   - Return user object (without password) and token
   - **Manual Test Step:** Use frontend register page → account created, redirected to onboarding
   - **User Test Prompt:** "Go to /register, create a new account with email and password. Confirm you're redirected to the onboarding page."

3. **Implement login endpoint with JWT generation**
   - Create login route in `backend/routers/auth.py`
   - Validate email and password against database
   - Verify password using Argon2
   - Generate JWT token with user ID and expiration
   - Return user object and token
   - **Manual Test Step:** Use frontend login page → logged in, redirected to dashboard/onboarding
   - **User Test Prompt:** "Go to /, log in with your credentials. Confirm you're redirected to the appropriate page based on whether you have a profile."

4. **Implement logout endpoint**
   - Create logout route (client-side token removal)
   - Return success message
   - **Manual Test Step:** Click logout button → redirected to login, protected pages inaccessible
   - **User Test Prompt:** "After logging in, click the Logout button. Confirm you're redirected to the login page and cannot access /onboarding or /results without logging in again."

5. **Implement `/auth/me` endpoint and JWT middleware**
   - Create JWT verification dependency in `backend/auth.py`
   - Extract and validate JWT from `Authorization: Bearer <token>` header
   - Create `/auth/me` endpoint that returns current user info
   - **Manual Test Step:** Frontend loads user info on app start → user name displayed
   - **User Test Prompt:** "Log in and refresh the page. Confirm your name appears in the header without needing to log in again."

6. **Update frontend AuthContext to use backend APIs**
   - Replace localStorage auth logic with API calls
   - Store JWT token in localStorage
   - Add token to all authenticated requests
   - Handle 401 errors by redirecting to login
   - **Manual Test Step:** Complete auth flow end-to-end → all features work
   - **User Test Prompt:** "Test the complete flow: register → onboarding → logout → login → results. Confirm all steps work correctly."

**Definition of Done:**
- Users can register via frontend
- Users can log in and receive JWT token
- Users can log out and session ends
- Protected routes require valid JWT
- Frontend stores and sends JWT correctly

**Post-Sprint:**
- Commit all changes with message: "S1: Authentication complete"
- Push to `main` branch

---

## 🧱 S2 – Financial Profile Management

**Objectives:**
- Store user financial profiles in MongoDB
- Create and update profile via API
- Retrieve user's profile for calculations

**User Stories:**
- As a user, I can save my financial information so I don't have to re-enter it
- As a user, I can update my profile to see updated projections
- As a user, my profile persists across devices

**Endpoints:**
- `POST /api/v1/profiles`
- `GET /api/v1/profiles/me`

**Tasks:**

1. **Create Profile Pydantic model and MongoDB schema**
   - Create `backend/models/profile.py` with Pydantic v2 model
   - Fields match frontend `UserFinancialProfile` type exactly
   - Add validation: numeric fields >= 0, zipCode 5 digits, childcarePreference enum
   - **Manual Test Step:** Import model in Python shell → no errors
   - **User Test Prompt:** "Run `python -c 'from backend.models.profile import Profile; print(Profile)'` and confirm no import errors."

2. **Implement POST `/api/v1/profiles` endpoint**
   - Create `backend/routers/profiles.py` with create/update route
   - Require JWT authentication
   - Check if user already has profile (upsert logic)
   - Validate all fields
   - Insert or update profile in `profiles` collection
   - Return complete profile object
   - **Manual Test Step:** Complete onboarding form → profile saved, redirected to results
   - **User Test Prompt:** "Log in, go to /onboarding, fill out all three steps, and submit. Confirm you're redirected to /results."

3. **Implement GET `/api/v1/profiles/me` endpoint**
   - Create route to fetch current user's profile
   - Require JWT authentication
   - Query `profiles` collection by `user_id`
   - Return profile or 404 if not found
   - **Manual Test Step:** Log in with existing profile → profile data loads in onboarding form
   - **User Test Prompt:** "Log in with an account that has a profile. Click 'Edit Inputs' and confirm the form is pre-filled with your saved data."

4. **Update frontend to use profile API**
   - Replace localStorage profile logic with API calls
   - Call `GET /api/v1/profiles/me` on app load
   - Call `POST /api/v1/profiles` on form submit
   - Handle loading states and errors
   - **Manual Test Step:** Create profile, logout, login on different browser → profile loads
   - **User Test Prompt:** "Create a profile, log out, then log in using a different browser or incognito window. Confirm your profile data is still there."

**Definition of Done:**
- Users can create financial profiles via frontend
- Users can update existing profiles
- Profiles persist in MongoDB
- Profiles load correctly across sessions and devices

**Post-Sprint:**
- Commit all changes with message: "S2: Profile management complete"
- Push to `main` branch

---

## 🧱 S3 – Projection Calculation & Warnings

**Objectives:**
- Implement 5-year projection calculation engine
- Generate financial warnings based on projection data
- Return complete projection object to frontend

**User Stories:**
- As a user, I want accurate 5-year projections so I can plan financially
- As a user, I want warnings about potential issues so I can prepare
- As a user, I want calculations to match the frontend logic exactly

**Endpoints:**
- `POST /api/v1/projections/calculate`

**Tasks:**

1. **Port expense assumptions logic to backend**
   - Create `backend/utils/expense_assumptions.py`
   - Port `getBabyExpenseAssumptions()` from frontend
   - Port childcare cost lookup by ZIP code
   - Include one-time costs and recurring costs data
   - **Manual Test Step:** Run unit test with sample ZIP → correct cost band returned
   - **User Test Prompt:** "Run `python -c 'from backend.utils.expense_assumptions import get_expense_assumptions; print(get_expense_assumptions(\"10001\"))'` and confirm it returns cost data."

2. **Implement projection calculation engine**
   - Create `backend/utils/projection_calculator.py`
   - Port `calculateFiveYearProjection()` from frontend
   - Calculate 60 monthly projections with income and expenses
   - Account for parental leave impact on income
   - Calculate childcare costs based on preference and start month
   - Aggregate into yearly projections
   - **Manual Test Step:** Calculate projection with test data → matches frontend output
   - **User Test Prompt:** "Use the same profile data in both frontend and backend. Confirm the total 5-year cost matches exactly."

3. **Implement warning generation logic**
   - Port `generateWarnings()` from frontend
   - Check for negative cashflow months
   - Check for low savings buffer
   - Check for high childcare costs
   - Check for parental leave impact
   - Return warnings with severity levels
   - **Manual Test Step:** Create profile with negative cashflow → warning appears
   - **User Test Prompt:** "Create a profile with low income and high expenses. Confirm warnings appear on the results page."

4. **Create POST `/api/v1/projections/calculate` endpoint**
   - Create `backend/routers/projections.py`
   - Require JWT authentication
   - Fetch user's profile from database
   - Calculate projection using profile data
   - Return complete projection object
   - **Manual Test Step:** Submit onboarding form → projection displays on results page
   - **User Test Prompt:** "Complete the onboarding form and submit. Confirm the results page shows your 5-year projection with all details."

5. **Update frontend to use projection API**
   - Replace frontend calculation with API call
   - Call `POST /api/v1/projections/calculate` on results page load
   - Display loading state during calculation
   - Handle errors gracefully
   - **Manual Test Step:** Navigate to results page → projection loads from backend
   - **User Test Prompt:** "Go to /results and confirm the projection loads. Check the Network tab to verify the data comes from the backend API."

**Definition of Done:**
- Backend calculates projections matching frontend logic exactly
- Warnings generate correctly based on projection data
- Frontend displays backend-calculated projections
- All projection features work end-to-end

**Post-Sprint:**
- Commit all changes with message: "S3: Projection calculation complete"
- Push to `main` branch

---

## 🧱 S4 – AI Summary Generation

**Objectives:**
- Integrate OpenAI API for summary generation
- Generate empathetic summaries using only calculated numbers
- Return markdown-formatted summaries to frontend

**User Stories:**
- As a user, I want an AI summary so I can understand my projection easily
- As a user, I want the summary to be empathetic and supportive
- As a user, I want the summary to use only my actual calculated numbers

**Endpoints:**
- `POST /api/v1/summaries/generate`

**Tasks:**

1. **Create OpenAI integration module**
   - Create `backend/integrations/openai_client.py`
   - Initialize OpenAI client with `OPENAI_API_KEY`
   - Create function to call chat completion API
   - Use `gpt-4o-mini` model for cost efficiency
   - **Manual Test Step:** Test API call with sample prompt → response received
   - **User Test Prompt:** "Run `python -c 'from backend.integrations.openai_client import test_connection; test_connection()'` and confirm OpenAI API responds."

2. **Create summary generation prompt template**
   - Create `backend/utils/summary_generator.py`
   - Build structured prompt with projection data
   - Include instructions to use only calculated numbers
   - Include empathetic tone guidelines
   - Format output as markdown
   - **Manual Test Step:** Generate summary with test data → markdown output received
   - **User Test Prompt:** "Generate a summary and confirm it's formatted as markdown with proper sections."

3. **Implement POST `/api/v1/summaries/generate` endpoint**
   - Create `backend/routers/summaries.py`
   - Require JWT authentication
   - Accept projection object in request body
   - Call OpenAI API with projection data
   - Return markdown summary
   - Handle API errors gracefully
   - **Manual Test Step:** View results page → AI summary displays
   - **User Test Prompt:** "Go to /results and confirm the AI summary appears in the 'Financial Blueprint' tab."

4. **Update frontend to use summary API**
   - Replace frontend summary generation with API call
   - Call `POST /api/v1/summaries/generate` after projection loads
   - Display loading state during generation
   - Show error message if generation fails
   - **Manual Test Step:** Navigate to results page → summary loads from backend
   - **User Test Prompt:** "Go to /results and wait for the AI summary to load. Confirm it appears and uses your actual calculated numbers."

**Definition of Done:**
- OpenAI API integration works correctly
- Summaries generate using only calculated projection data
- Summaries display in markdown format on frontend
- Error handling works for API failures

**Post-Sprint:**
- Commit all changes with message: "S4: AI summary generation complete"
- Push to `main` branch

---

## 🧱 S5 – PDF Export

**Objectives:**
- Generate PDF documents from projection and summary
- Include all projection details, warnings, and assumptions
- Enable download via frontend

**User Stories:**
- As a user, I can download my projection as PDF so I can save and share it
- As a user, the PDF includes all my projection details and AI summary
- As a user, the PDF has a professional layout

**Endpoints:**
- `POST /api/v1/exports/pdf`

**Tasks:**

1. **Create PDF generation utility**
   - Create `backend/utils/pdf_generator.py`
   - Use `reportlab` library for PDF creation
   - Create function to generate PDF from projection and summary
   - Include: executive summary, year-by-year breakdown, warnings, AI summary, assumptions
   - Format with basic professional layout
   - **Manual Test Step:** Generate PDF with test data → PDF file created
   - **User Test Prompt:** "Generate a test PDF and open it. Confirm it contains all projection data in a readable format."

2. **Implement POST `/api/v1/exports/pdf` endpoint**
   - Create `backend/routers/exports.py`
   - Require JWT authentication
   - Accept projection and summary in request body
   - Generate PDF using utility function
   - Return PDF as binary response with appropriate headers
   - Set filename: `nestworth-plan-{date}.pdf`
   - **Manual Test Step:** Click "Download PDF" button → PDF downloads
   - **User Test Prompt:** "Go to /results and click 'Download PDF'. Confirm a PDF file downloads with your projection data."

3. **Update frontend to use PDF export API**
   - Replace `window.print()` with API call
   - Call `POST /api/v1/exports/pdf` with projection and summary
   - Handle binary response and trigger download
   - Show loading state during generation
   - **Manual Test Step:** Download PDF → opens correctly with all data
   - **User Test Prompt:** "Download the PDF and open it. Confirm it includes your complete projection, warnings, AI summary, and assumptions."

**Definition of Done:**
- PDF generation works correctly
- PDFs include all projection data and AI summary
- PDFs download via frontend with correct filename
- PDF layout is professional and readable

**Post-Sprint:**
- Commit all changes with message: "S5: PDF export complete"
- Push to `main` branch

---

## ✅ Style & Compliance Checks

- ✅ Bullets only — no tables or prose
- ✅ Only visible frontend features included
- ✅ Minimal APIs/models aligned with UI
- ✅ MongoDB Atlas only (no local instance)
- ✅ Python 3.13 runtime specified
- ✅ Each task has manual test step
- ✅ After all tests pass → commit & push to `main`
- ✅ API base path `/api/v1/*`
- ✅ No Docker deployment
- ✅ Single Git branch `main` only
- ✅ Manual testing after every task (not only after sprints)

---

## 🎯 Final Notes

**Development Workflow:**
1. Complete each task in order
2. Test manually via frontend UI after each task
3. Fix any issues before proceeding to next task
4. After all sprint tasks pass, commit and push to `main`
5. Move to next sprint

**Testing Emphasis:**
- Every task must be tested via frontend UI
- No automated tests required for MVP
- Manual testing ensures real-world functionality
- User test prompts provide clear testing instructions

**Git Workflow:**
- Single branch `main` only
- Commit after each sprint completion
- Push to GitHub after verification
- No feature branches or pull requests needed for MVP

**Success Metrics:**
- All frontend features work with backend
- User data persists correctly
- Projections match frontend calculations exactly
- AI summaries generate successfully
- PDFs export correctly