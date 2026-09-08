# BillSplit — Project Master Context

## 1. Project Goal

Build a web application that takes one or more photographs of a restaurant bill and helps a group accurately split the bill.

The core flow is:

Upload bill photos
→ AI/vision extracts structured bill data
→ Human reviews and corrects extraction
→ User adds people
→ User assigns each item to one or more people
→ Deterministic backend calculates each person's share
→ Detailed per-person breakdown is displayed

The application is intended to solve real-world bill splitting, especially when bills contain:

* taxes
* GST
* service charges
* discounts
* shared dishes
* quantities
* multiple people
* poor-quality photographs
* multiple bill photographs

---

# 2. Core Product Principle

The application follows a strict human-in-the-loop architecture:

AI reads the bill.

Human verifies/corrects the extracted information.

Deterministic application code performs all financial calculations.

The AI must NEVER determine the final amount owed by each person.

This separation is intentional because financial calculations must be predictable, testable and explainable.

---

# 3. MVP Scope

The MVP DOES include:

* Upload one or more bill photographs
* AI/vision-based bill extraction
* Structured Pydantic representation
* Per-field confidence
* Human review/editing
* Add people
* Assign items to people
* Shared item splitting
* "Everyone" assignment
* Proportional tax allocation
* Proportional service-charge allocation
* Discount handling
* Monetary rounding/reconciliation
* Printed-total validation
* Detection of arithmetic inconsistencies
* Detailed per-person final breakdown
* Support for a bill spanning two photographs

The MVP DOES NOT include:

* User accounts
* Authentication
* Authorization
* Database
* Persistent bill history
* Friends
* Groups
* Payments
* Notifications
* Chatbot
* Social features
* Microservices
* Redis
* Kafka
* Background job infrastructure

Do not introduce these unless explicitly requested.

---

# 4. Architecture

Use a simple stateless architecture:

Frontend
↓
FastAPI backend
↓
Vision/AI extraction service

and:

Frontend
↓
FastAPI backend
↓
Deterministic validation/calculation services

There is no database.

Bills exist only for the duration of the user's workflow.

The frontend can temporarily hold the reviewed bill state and send it back to the backend for calculation.

---

# 5. Recommended Stack

Frontend:

* React
* TypeScript
* TailwindCSS

Backend:

* Python
* FastAPI
* Pydantic

Testing:

* pytest

Use Decimal or integer paise/cents for financial calculations.

Do NOT use floating-point arithmetic for final monetary calculations.

---

# 6. Backend Structure

Use a small, modular structure:

backend/
└── app/
├── main.py
│
├── schemas/
│   ├── bill.py
│   └── split.py
│
├── routers/
│   ├── extraction.py
│   └── split.py
│
└── services/
├── extraction.py
├── validation.py
└── calculator.py

Tests:

backend/
└── tests/
├── test_calculator.py
└── test_validation.py

Do not create unnecessary abstraction layers such as repositories, database models, dependency containers, or service interfaces unless they become genuinely necessary.

---

# 7. Domain Model

A bill contains:

Bill

* restaurant_name
* currency
* items
* subtotal
* discount
* service_charge
* tax
* printed_total
* calculated_total
* validation information

Each item contains:

BillItem

* id
* name
* quantity
* unit_price
* total_price
* confidence information

A bill may have multiple images/pages.

The application should treat multiple uploaded images as pages of the same bill.

---

# 8. Pydantic Extraction Schema

The AI extraction output must be structured JSON.

Conceptually:

BillItem:

* id
* name
* quantity
* unit_price
* total_price
* confidence

BillExtraction:

* restaurant_name
* currency
* items
* subtotal
* discount
* service_charge
* tax
* printed_total
* confidence

Confidence must be available per extracted field.

Example:

{
"name": "Chicken Biryani",
"quantity": 2,
"unit_price": 350,
"total_price": 700,
"confidence": {
"name": 0.97,
"quantity": 0.99,
"unit_price": 0.94,
"total_price": 0.98
}
}

If something is not visible or cannot be reliably extracted, return null rather than inventing a value.

---

# 9. AI Extraction Responsibilities

The vision model is responsible only for perception/extraction.

It should:

* Read the bill
* Identify line items
* Extract quantities
* Extract prices
* Extract subtotal
* Extract discounts
* Extract service charges
* Extract taxes
* Extract printed total
* Handle multiple photographs
* Provide confidence values

It should NOT:

* Decide who consumed an item
* Split items between people
* Decide tax allocation
* Decide service-charge allocation
* Calculate the final amount owed
* Silently correct suspicious bill arithmetic

Use structured JSON output matching the Pydantic schema.

The extraction prompt should explicitly tell the model not to invent missing information.

---

# 10. Human Review Stage

The extracted bill must be shown to the user before calculation.

The user must be able to edit:

* item name
* quantity
* unit price
* item total
* subtotal
* discount
* service charge
* tax
* printed total

Low-confidence fields should be visually highlighted.

No final bill calculation should happen using unreviewed AI output.

The reviewed data becomes the source of truth for the calculation stage.

---

# 11. Bill Validation

The backend must independently validate the reviewed bill.

Checks should include:

1. Quantity × unit price ≈ line total

2. Sum of line-item totals ≈ subtotal

3. Subtotal - discount + service charge + tax ≈ calculated total

4. Compare calculated total with printed total

Do NOT silently modify the user's data when validation fails.

Instead, return warnings.

Example:

{
"status": "warning",
"messages": [
"Printed total does not match calculated total.",
"Expected: ₹1180",
"Printed: ₹1250",
"Difference: ₹70"
]
}

The user should be able to see the discrepancy.

---

# 12. The Incorrect-Bill Requirement

At least one test bill will intentionally contain an incorrect printed total.

The application must detect this.

Example:

Items:
₹1000

GST:
₹180

Expected total:
₹1180

Printed total:
₹1250

The application should display:

"Bill arithmetic mismatch"

Expected total: ₹1180
Printed total: ₹1250
Difference: ₹70

Do not automatically replace the printed total.

---

# 13. People and Assignments

After review, the user adds people.

Example:

People:

* Yash
* Rahul
* Aman

Each bill item can be assigned to:

* exactly one person
* multiple people
* everyone

Represent assignments explicitly.

Example:

Chicken Biryani → Yash + Rahul

Coke → Aman

Naan → Everyone

---

# 14. Item Splitting Rules

If an item belongs to one person:

100% goes to that person.

If an item belongs to multiple people:

Split equally unless custom shares are explicitly supported.

If an item belongs to everyone:

Split equally among all people.

Example:

Biryani = ₹600

Yash + Rahul:

Yash = ₹300
Rahul = ₹300

If Naan = ₹200 and three people ate it:

₹200 / 3

The rounding system must ensure that the individual shares sum exactly to ₹200.

---

# 15. Tax Allocation

Tax must NOT be divided equally among the number of people.

Tax is allocated proportionally based on each person's pre-tax consumption.

Example:

Yash = ₹500 of food

Rahul = ₹300

Aman = ₹200

Total = ₹1000

GST = ₹180

Therefore:

Yash:
500 / 1000 × 180 = ₹90

Rahul:
300 / 1000 × 180 = ₹54

Aman:
200 / 1000 × 180 = ₹36

Total GST allocated = ₹180.

---

# 16. Service Charge Allocation

Service charge follows the same proportional rule.

If:

Yash consumes ₹500
Rahul consumes ₹300
Aman consumes ₹200

and service charge = ₹100:

Yash = ₹50
Rahul = ₹30
Aman = ₹20

Never simply divide service charge by number of people.

---

# 17. Discount Handling

Implement one clearly defined discount policy.

Default policy:

Allocate a bill-level discount proportionally according to each person's pre-discount consumption.

Example:

Consumption:

Yash = ₹500
Rahul = ₹300
Aman = ₹200

Discount = ₹100

Then:

Yash receives ₹50 discount
Rahul receives ₹30
Aman receives ₹20

Document the policy clearly in the code and UI.

Do not invent complex discount rules unless required.

---

# 18. Money Handling

Never rely on binary floating point for final monetary values.

Prefer integer paise/cents internally.

Example:

₹123.45 → 12345 paise

All splitting, tax allocation, service-charge allocation and rounding should operate on integer monetary units.

When dividing amounts:

* calculate base shares
* distribute remainder deterministically
* ensure the sum of shares exactly equals the original amount

Invariant:

sum(person amounts) == bill amount being allocated

There must be no ₹0.01/₹0.02 reconciliation errors.

---

# 19. Calculator

All financial business logic must live in one deterministic calculator module.

Conceptually:

calculate_split(
bill,
people,
assignments
)

The calculator should:

1. Calculate each item's share
2. Aggregate each person's pre-tax consumption
3. Apply discounts
4. Allocate service charge proportionally
5. Allocate taxes proportionally
6. Reconcile rounding
7. Produce final per-person totals

The calculator must not depend on the AI provider.

The calculator should be independently unit-testable.

Same input must always produce the same output.

---

# 20. API Design

Keep the API minimal.

Potential endpoints:

POST /extract

* receive bill image(s)
* return structured extraction

POST /validate

* receive reviewed bill
* return validation results

POST /calculate

* receive reviewed bill + people + assignments
* return final breakdown

There is no need for bill IDs backed by a database.

Do not introduce CRUD endpoints for persistent bills.

---

# 21. Frontend Flow

Only four major screens are needed.

## Screen 1 — Upload

Allow:

* one photograph
* multiple photographs
* preview/remove images
* submit for extraction

## Screen 2 — Review

Show:

* extracted items
* quantities
* prices
* subtotal
* discount
* service charge
* tax
* total
* confidence indicators
* validation warnings

Allow editing.

Button:

"Confirm Bill"

## Screen 3 — Assignment

Allow:

* adding people
* assigning each item to one or more people
* assigning an item to everyone

Keep interaction simple.

Checkboxes are sufficient.

## Screen 4 — Results

Show detailed per-person breakdown.

For each person show:

* individual items
* shared item portions
* subtotal consumed
* discount
* allocated tax
* allocated service charge
* final amount

Also show a reconciliation summary:

Total bill: ₹X
Total allocated: ₹X
Difference: ₹0

---

# 22. Explainability

Every calculated amount should be explainable.

Example:

Chicken Biryani — ₹700
Shared by Yash + Rahul

Yash → ₹350
Rahul → ₹350

GST:

Total GST → ₹180

Yash consumed 50% of the pre-tax bill.

Yash's GST → ₹90.

The UI should make it obvious why each person owes their final amount.

---

# 23. Advanced Features Worth Implementing

Prioritize these only after the core workflow works:

1. Low-confidence field highlighting

2. Arithmetic anomaly detection

3. Multi-photo bill support

4. Explainable tax/service-charge allocation

5. Custom item shares

6. Confidence-based review suggestions

For example:

"3 fields have low confidence and may need review."

Do not add unrelated features.

---

# 24. Test Dataset

Create at least 12 real bills.

Include deliberately difficult conditions:

* dim lighting
* crumpled paper
* steep camera angle
* faded thermal print
* handwriting
* two scripts
* long bill requiring two photographs
* crowded receipt
* complicated taxes
* multiple quantities
* shared items
* one bill with an incorrect printed total

Manually create ground-truth JSON for each bill.

Example:

tests/
└── fixtures/
├── bill01.json
├── bill02.json
└── ...

The ground truth is used to evaluate extraction quality.

---

# 25. Testing Strategy

Prioritize deterministic tests over UI tests.

Calculator tests should cover:

* single-person item
* two-person shared item
* everyone assignment
* odd-cent/paise division
* proportional GST
* proportional service charge
* discount allocation
* zero tax
* zero service charge
* multiple taxes
* rounding remainder
* total reconciliation

Validation tests should cover:

* correct subtotal
* incorrect subtotal
* correct total
* incorrect printed total
* quantity × price mismatch

Extraction evaluation should compare AI output against the manually labelled ground truth.

---

# 26. Development Strategy

Build in this order:

PHASE 1
Deterministic calculator

PHASE 2
Validation engine

PHASE 3
FastAPI endpoints

PHASE 4
Frontend with mocked extraction data

PHASE 5
Real vision extraction

PHASE 6
Human review UI

PHASE 7
Assignment UI

PHASE 8
Final results UI

PHASE 9
Testing against 12 real bills

PHASE 10
Visual polish and advanced features

Do not start with the AI integration.

First make sure the application's core mathematics is correct.

---

# 27. Coding-Agent Rules

When working on this project:

* Read this file before making architectural decisions.
* Do not rebuild working code unnecessarily.
* Make the smallest coherent change for each task.
* Do not introduce new dependencies unless necessary.
* Do not introduce a database.
* Do not introduce authentication.
* Do not introduce microservices.
* Do not move business logic into the frontend.
* Do not duplicate calculator logic.
* Keep financial calculations deterministic.
* Use tests for financial logic.
* Preserve existing APIs unless a breaking change is explicitly requested.
* Before modifying an existing file, inspect its current implementation.
* If a requirement is ambiguous, prefer the simplest implementation consistent with this document.

When asked to implement something, modify only the files necessary for that task and briefly explain what changed and how it was verified.

---

# 28. Fundamental Architecture Principle

The system has three distinct responsibilities:

AI:
"What does the bill say?"

Human:
"Is that what the bill actually says?"

Code:
"Given the verified data, who owes how much?"

Do not blur these responsibilities.
