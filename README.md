# Book Metadata and Recommendation API

A FastAPI coursework project focused on a runnable, SQL-backed API with authentication, analytics, tests, and clean repository structure.

## Why this project suits the brief
- Implements a complete SQL-backed CRUD API
- Exposes more than four HTTP endpoints
- Returns JSON and uses conventional HTTP status codes
- Includes authentication, analytics, and recommendation functionality
- Provides tests and sample data import support

## Core features
- CRUD for books
- Read access for users
- Authenticated CRUD for reviews
- JWT authentication (`/auth/register`, `/auth/login`)
- Analytics endpoints:
  - `/analytics/top-rated-books`
  - `/analytics/genre-distribution`
  - `/analytics/most-reviewed-books`
  - `/analytics/books-per-year`
  - `/analytics/recommendations/{user_id}`

## Tech stack
- FastAPI
- SQLAlchemy
- PostgreSQL (recommended for submission)
- SQLite (default local fallback for easy testing)
- JWT with `python-jose`
- Pytest

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The application loads configuration automatically from `.env`, so database, auth, and documentation settings can be changed without editing source code.

API docs will be available at:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Populate sample data
```bash
python scripts/import_books.py scripts/sample_books.csv
```

## Run tests
```bash
pytest
```

## Recommended deployment
Deploy the API on Render, Railway, or PythonAnywhere with PostgreSQL. For the oral exam, have both the hosted deployment and local fallback ready.

## Current repository scope
This GitHub version is intentionally code-first while the coursework deliverables are still being refined.

Included now:
- API source code
- Tests
- Import script and sample CSV data
- Setup instructions and environment template

To be added later for final coursework submission:
- API documentation PDF
- Technical report PDF
- Presentation slides
