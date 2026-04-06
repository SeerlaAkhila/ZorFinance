# Python Finance System Backend

Simple, clean FastAPI project for finance record management, summaries, and role-based behavior.
This solution is intentionally minimal and assessment-friendly.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- SQLite (default persistence)
- Pydantic (validation)

## What Is Included

### 1) Financial Records Management

- Create, read, update, delete financial records.
- Each record includes:
  - `amount`
  - `type` (`income` / `expense`)
  - `category`
  - `date`
  - `notes`
  - `owner_id`
- Filtering supported on list endpoint:
  - `type`
  - `category`
  - `start_date`
  - `end_date`
- Pagination supported with `skip` and `limit`.

### 2) Summary and Analytics Logic

- Overview:
  - Total income
  - Total expenses
  - Current balance
  - Total records
- Category-wise breakdown.
- Monthly totals (income, expenses, net).
- Recent activity feed.

### 3) User and Role Handling

- Roles:
  - `viewer`: view records + basic summary.
  - `analyst`: viewer permissions + detailed analytics.
  - `admin`: full CRUD on records + user management.
- Simplified auth via `X-User-Id` request header.
- Seeded users for immediate testing:
  - `1` -> Viewer
  - `2` -> Analyst
  - `3` -> Admin

### 4) Validation and Error Handling

- Input validation via Pydantic:
  - positive amount
  - bounded field lengths
  - enum constraints
- Business validation:
  - `start_date <= end_date`
- Meaningful HTTP responses:
  - `401` for missing/invalid user header
  - `403` for permission violations
  - `404` for missing resources
  - `422` for invalid request payload/filter combinations

## Project Structure

```text
app/
  config.py
  db.py
  dependencies.py
  main.py
  models.py
  schemas.py
  seed.py
  routers/
    records.py
    summaries.py
    users.py
requirements.txt
README.md
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- App UI: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs` (only if `ENABLE_DOCS=true`)
- ReDoc: `http://127.0.0.1:8000/redoc`

To enable API docs:

```bash
set ENABLE_DOCS=true
uvicorn app.main:app --reload
```

## 5-Minute Evaluation Flow

1. Start server and open `http://127.0.0.1:8000/`.
2. Use seeded users from role switch:
   - `1` Viewer
   - `2` Analyst
   - `3` Admin
3. As Admin, create a few income and expense records.
4. Test filters (type/category/date).
5. Check overview summary cards and analytics endpoints.
6. Switch role to Viewer/Analyst and verify access behavior.

## API Examples

Use `X-User-Id: 3` for admin actions.

Create record:

```bash
curl -X POST "http://127.0.0.1:8000/records" ^
  -H "Content-Type: application/json" ^
  -H "X-User-Id: 3" ^
  -d "{\"amount\":12500.00,\"type\":\"income\",\"category\":\"salary\",\"date\":\"2026-04-01\",\"notes\":\"April salary\"}"
```

List records with filters:

```bash
curl "http://127.0.0.1:8000/records?type=expense&start_date=2026-04-01&end_date=2026-04-30" ^
  -H "X-User-Id: 1"
```

Overview summary:

```bash
curl "http://127.0.0.1:8000/summaries/overview" ^
  -H "X-User-Id: 1"
```

Detailed analytics (analyst/admin):

```bash
curl "http://127.0.0.1:8000/summaries/monthly-totals" ^
  -H "X-User-Id: 2"
```

## Assumptions

- Authentication is intentionally simplified to focus on backend design and business logic.
- Admin can create records for any user (`owner_id`) or default to self.
- Currency is not modeled as a separate field; amounts are treated as decimal financial values.
- SQLite is default for easy local setup; database URL can be overridden with `DATABASE_URL`.
- API docs are hidden by default for non-technical usage; set `ENABLE_DOCS=true` to expose `/docs` and `/redoc`.

## Intentionally Kept Simple

- No JWT/session auth (uses `X-User-Id` header for easy testing).
- No background jobs, queues, or complex architecture.
- No unnecessary abstractions; focus is on correctness and readability.

## How This Fits the Assignment

- Covers full backend CRUD + filtering + analytics logic.
- Demonstrates role-based behavior with clear access boundaries.
- Uses ORM-based persistence and structured validation/error handling.
- Keeps architecture simple but clean and extensible.
