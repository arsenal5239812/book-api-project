# Book Metadata and Recommendation API

A coursework-ready FastAPI project designed for a high-mark oral examination submission. It demonstrates CRUD, SQL persistence, authentication, analytics, testing, documentation, and deployment readiness.

## Why this project suits the brief
- Implements a complete SQL-backed CRUD API
- Exposes more than four HTTP endpoints
- Returns JSON and uses conventional HTTP status codes
- Includes authentication, analytics, and recommendation functionality
- Provides tests, documentation, a report draft, and presentation slides

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

## Repository checklist for submission
- [x] Public GitHub repository
- [x] Visible commit history
- [x] README with setup and overview
- [x] API documentation draft
- [x] Technical report draft
- [x] Presentation slide deck
- [x] Tests
- [x] Import script and sample data

## Suggested commit plan
1. `init fastapi project structure`
2. `add sql models and schemas`
3. `implement auth endpoints`
4. `implement book crud`
5. `implement review permissions and analytics`
6. `add tests and seed script`
7. `write docs report and slides`

## Files included
- `docs/api_documentation.pdf`
- `report/technical_report.pdf`
- `slides/book_api_presentation.pptx`
