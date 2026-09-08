# BillSplit

> **AI-powered bill splitting with a human in the loop.**

BillSplit turns restaurant bill photos into transparent, verifiable
splits between friends.

The system uses AI for **bill perception**, a human for
**verification**, and deterministic application logic for **validation
and financial calculations**.

------------------------------------------------------------------------

## ✨ Why BillSplit?

Restaurant bill splitting becomes complicated when a bill contains:

-   Different items ordered by different people
-   Items shared between multiple people
-   Taxes and service charges
-   Discounts
-   Round-off or adjustment amounts
-   Difficult-to-read receipts
-   Incorrect printed totals

BillSplit is built around one principle:

> **AI reads the bill. Humans verify it. Code does the arithmetic.**

------------------------------------------------------------------------

## 🚀 How It Works

``` text
┌─────────────┐
│ Upload Bill │
│ JPG/PNG/WebP│
└──────┬──────┘
       ↓
┌────────────────────┐
│ Gemini Vision      │
│ Structured Extract │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Human Review       │
│ Verify & Correct   │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Deterministic      │
│ Validation         │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Assign Items       │
│ to 2–7 people      │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Deterministic      │
│ Split Calculation  │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Detailed Results   │
└────────────────────┘
```

### 1. Upload

Upload one or more photos of the same bill.

### 2. AI Extraction

Gemini Vision extracts:

-   Restaurant name
-   Currency
-   Items
-   Quantity
-   Unit price
-   Line total
-   Subtotal
-   Discount
-   Service charge
-   Taxes
-   Adjustment / round-off
-   Printed total

Each extracted field carries its own **confidence score**.

### 3. Human Verification

The extracted bill is presented in an editable review screen.

Users can verify and correct extracted quantities, prices, line totals,
subtotal, discount, service charge, adjustment, and printed total before
calculation.

Confidence scores are informational only and never determine whether a
value is accepted.

### 4. Validation

The backend deterministically checks:

-   `quantity × unit price = line total`
-   Line totals reconcile with the subtotal
-   Subtotal, discount, service charge, taxes, and adjustment reconcile
    with the calculated total
-   Printed total matches the calculated total

A printed-total mismatch is surfaced as a warning rather than silently
corrected.

### 5. Assignment

Add **2-7 people** and assign each item to:

-   One person
-   Multiple people
-   Everyone

Shared items are split equally.

### 6. Calculation

The backend performs financial calculations using **integer
paise/cents**, avoiding floating-point money errors.

Discounts, taxes, service charges, and adjustments are allocated
deterministically and reconciled exactly.

### 7. Results

Each person receives a detailed breakdown of:

-   Items they owe for
-   Subtotal share
-   Discount
-   Service charge
-   Tax
-   Adjustment
-   Final amount

------------------------------------------------------------------------

## 🤖 AI + Human-in-the-Loop

BillSplit deliberately separates **perception** from **computation**.

### Gemini

Gemini handles:

-   Reading bill images
-   Extracting visible values
-   Combining multiple images of a bill
-   Difficult lighting and perspective
-   Faded thermal printing
-   Handwriting
-   Multiple scripts or languages
-   Field-level confidence estimation

### Application Logic

The application handles:

-   Bill validation
-   Shared-item splitting
-   Person assignments
-   Proportional charge allocation
-   Exact financial arithmetic
-   Reconciliation
-   Printed-total discrepancy detection

This separation keeps probabilistic AI away from the final financial
calculations.

------------------------------------------------------------------------

## 📊 Field-Level Confidence

Confidence is tracked independently for extracted fields.

Example:

``` text
Item name       97%
Quantity        99%
Unit price      84%
Line total      91%
```

A confidence score is an indication of extraction certainty, not a
guarantee of correctness. Human verification remains part of the
workflow.

------------------------------------------------------------------------

## 💰 Exact Money Handling

All monetary values are represented internally as **integer
paise/cents**.

``` text
₹123.45 → 12345 paise
```

Final financial calculations do not rely on floating-point arithmetic.

Allocation uses deterministic integer arithmetic with largest-remainder
handling so that the final allocations reconcile exactly:

``` text
sum(all individual shares) == bill total
```

------------------------------------------------------------------------

## 🧮 Splitting Rules

### Single-person item

The entire item is assigned to that person.

### Shared item

An item assigned to multiple people is split equally among them.

### Everyone

An item assigned to `everyone` is split equally across all people.

### Tax and service charge

Tax and service charge are distributed **proportionally to each person's
consumption**, rather than equally across people.

### Discount

Discount is distributed proportionally to consumption.

### Adjustment / round-off

A visible bill-level adjustment is preserved, including its sign, and
allocated deterministically.

------------------------------------------------------------------------

## 🔍 Validation & Wrong Totals

BillSplit does not assume that the printed total is correct.

For example:

``` text
Subtotal          ₹1,000
Tax                  ₹180
Printed total      ₹1,150
────────────────────────
Calculated total   ₹1,180
```

The discrepancy is surfaced for review rather than changing the printed
value or hiding the error.

------------------------------------------------------------------------

## 🏗️ Architecture

``` text
React + TypeScript + Tailwind
             │
             │ HTTP / JSON + multipart
             ▼
        FastAPI Backend
             │
      ┌──────┴──────┐
      ▼             ▼
 Gemini Vision   Deterministic
  Extraction      Validation
                     │
                     ▼
                Split Engine
```

### Backend

-   **FastAPI** --- API layer
-   **Pydantic** --- structured schemas and validation
-   **Google Gemini** --- bill image extraction
-   **Pillow** --- image validation
-   **pytest** --- backend testing

### Frontend

-   **React**
-   **TypeScript**
-   **Tailwind CSS**
-   **Vite**
-   **Lucide React**

------------------------------------------------------------------------

## 📁 Project Structure

``` text
BillSplit/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── bill.py
│   │   │   └── extraction.py
│   │   ├── schemas/
│   │   │   ├── bill.py
│   │   │   ├── extraction.py
│   │   │   ├── validation.py
│   │   │   └── split.py
│   │   ├── services/
│   │   │   ├── calculator.py
│   │   │   ├── extractor.py
│   │   │   └── validation.py
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── App.tsx
│   └── package.json
│
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

## 🛠️ Running Locally

### Prerequisites

-   Python 3.10+
-   Node.js 18+
-   A Gemini API key

### 1. Clone the repository

``` bash
git clone https://github.com/Yash-658/BillSplit.git
cd BillSplit
```

### 2. Set up the backend

Create a virtual environment:

``` bash
python -m venv .venv
```

Activate it:

**Windows**

``` bash
.venv\Scripts\activate
```

**macOS/Linux**

``` bash
source .venv/bin/activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

### 3. Configure Gemini

The backend reads these values from the process environment:

``` env
GEMINI_API_KEY=your_api_key_here
GEMINI_VISION_MODEL=your_supported_gemini_model
```

The application does not automatically load `.env` files, so set the
variables in your shell before starting the backend.

**Windows PowerShell:**

``` powershell
$env:GEMINI_API_KEY="your_api_key_here"
$env:GEMINI_VISION_MODEL="your_supported_gemini_model"
```

`GEMINI_VISION_MODEL` is optional and overrides the extractor's default
model, `gemini-2.5-flash-lite`.

Never commit API credentials.

### 4. Start the backend

From the project root:

``` bash
uvicorn backend.app.main:app --reload
```

Backend:

``` text
http://localhost:8000
```

Interactive API documentation:

``` text
http://localhost:8000/docs
```

### 5. Start the frontend

Open another terminal:

``` bash
cd frontend
npm install
npm run dev
```

Frontend:

``` text
http://localhost:5173
```

------------------------------------------------------------------------

## 🔌 API

  -----------------------------------------------------------------------
  Endpoint                            Purpose
  ----------------------------------- -----------------------------------
  `POST /extract`                     Extract structured bill data from
                                      one or more images

  `POST /validate`                    Validate the reviewed bill and its
                                      arithmetic

  `POST /calculate`                   Calculate the deterministic
                                      per-person split
  -----------------------------------------------------------------------

The backend is stateless for the current workflow, and the frontend
communicates with it over HTTP.

------------------------------------------------------------------------

## 🧪 Testing

Run the backend test suite from the project root:

``` bash
pytest -q
```

The test suite covers the deterministic calculator, validation engine,
API behavior, assignments, adjustments, reconciliation, and people-count
boundaries.

Build the frontend:

``` bash
cd frontend
npm run build
```

------------------------------------------------------------------------

## 📸 Real-Bill Evaluation

BillSplit's extraction pipeline is designed for evaluation across **12
real restaurant bills** representing challenging conditions:

-   Clear baseline receipts
-   Dim lighting
-   Crumpled bills
-   Steep camera angles
-   Faded thermal printing
-   Handwritten annotations
-   Multiple scripts/languages
-   Long bills requiring multiple photos
-   Crowded bills with many items
-   Complicated tax structures
-   Shared/multiple-quantity items
-   An intentionally incorrect printed total

The evaluation compares extracted values against manually established
ground truth at both bill and item level.

For the wrong-total case, the visible incorrect printed total should be
preserved by extraction while deterministic validation flags the
discrepancy.

------------------------------------------------------------------------

## 🎭 Demo Data

A `mockBill` fixture is retained in the frontend as a convenient
demo/start-over state.

The main Upload → Extract → Review → Validate → Assign → Calculate →
Results workflow uses the actual backend APIs.

The current MVP keeps bills transient rather than introducing persistent
application state, keeping the core bill-understanding and splitting
pipeline focused.

------------------------------------------------------------------------

## 🎯 Design Principles

### 1. AI for perception, not arithmetic

Vision models are probabilistic. Financial calculations should be
deterministic.

### 2. Human verification before calculation

Extracted values are presented for human review before the financial
engine uses them.

### 3. Preserve what is printed

If a bill visibly contains an incorrect total, BillSplit records it and
surfaces the discrepancy rather than silently correcting it.

### 4. Exact money

Integer paise/cents prevent floating-point rounding problems.

### 5. Explainability

Each final amount can be traced back to the items assigned to that
person and the bill-level charges allocated to them.

------------------------------------------------------------------------

## 🚧 Future Improvements

-   Low-confidence visual highlighting
-   Custom fractional shares for shared items
-   More detailed tax metadata
-   Automated benchmark dashboards
-   Improved duplicate-item matching
-   Persistent bill history
-   Authentication
-   Saved groups and friends
-   Payment integrations

------------------------------------------------------------------------

```{=html}
<p align="center">
```
`<strong>`{=html}BillSplit`</strong>`{=html}`<br>`{=html} Read the bill
with AI. Verify it with a human. Split it with deterministic math.
```{=html}
</p>
```
