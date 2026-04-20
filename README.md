# Book Metadata and Recommendation API

A FastAPI coursework project that exposes a SQL-backed API for book metadata, reviews, analytics, and explainable recommendations.

## Why this project suits the brief
- Implements a complete JSON API backed by a relational database
- Provides CRUD workflows, authentication, analytics, and recommendation features
- Uses version control, automated tests, and a reproducible local setup
- Supports both small manual datasets and a real public book dataset (`goodbooks-10k`)
- Keeps configuration outside business logic through environment-driven settings

## Current feature set
- Books:
  - Create, read, update, and delete books
  - Advanced filtering by genre, author, language, source, year range, rating, and ratings count
  - Provenance filtering by origin type, source platform, translation status, creation disclosure, moderation status, and AI risk score
  - Search, sorting, and pagination on `GET /books`
  - Dedicated provenance update workflow via `PUT /books/{book_id}/provenance`
  - Provenance-aware similar book discovery via `GET /books/{book_id}/similar`
- Users:
  - Register and log in with JWT
  - Read user listings and individual profiles
  - Read the authenticated user via `GET /users/me`
- Reviews:
  - Authenticated create, update, and delete
  - Duplicate-review protection for the same user/book pair
  - Filtering by book, user, minimum rating, and pagination
- Analytics:
  - Top-rated books
  - Genre distribution
  - Most-reviewed books
  - Books per year
  - Language distribution
  - Source distribution
  - Rating bands
  - Author performance
  - Publication decade distribution
  - Creation disclosure distribution
  - Moderation status distribution
  - Web novel translation distribution
  - User profile analytics
  - Explainable recommendations with ranking reasons and content-preference filtering

## Provenance and AI transparency layer
The API now includes a provenance metadata layer designed for platform-governance style scenarios rather than simple catalogue storage.

Each book can store:
- `origin_type`
- `source_platform`
- `original_language`
- `translation_status`
- `creation_disclosure`
- `disclosure_source`
- `moderation_status`
- `ai_risk_score`
- `provenance_notes`

This makes it possible to model:
- traditionally published books versus web novels
- translated versus original works
- human-only versus AI-assisted disclosure
- verified versus flagged provenance records

The recommendation endpoint can also apply a reader-facing content preference:
- `human_only`
- `allow_ai_assisted`
- `any`

The similar-book discovery endpoint also uses provenance-aware similarity scoring, so discovery is influenced by genre, language, source platform, moderation status, and content-origin metadata rather than only basic catalogue fields.

This allows the project to demonstrate not only recommendation logic, but also how provenance metadata can influence discovery and trust.

## Public dataset support
The project can import the public `goodbooks-10k` dataset to create a stronger demo for analytics and recommendation features.

## Dataset source declaration
The real public dataset used by this project is `goodbooks-10k`.

Source references:
- Kaggle dataset page: [goodbooks-10k](https://www.kaggle.com/datasets/zygmunt/goodbooks-10k)
- Upstream source used by the importer: [zygmuntz/goodbooks-10k](https://github.com/zygmuntz/goodbooks-10k)

This project downloads the CSV files from the upstream GitHub repository because the importer needs direct file URLs for `books.csv`, `tags.csv`, and `book_tags.csv`.

Imported metadata includes:
- `ratings_count`
- `isbn13`
- `language_code`
- `source`

Manually curated provenance fields can then be added through the API to support web-novel origin tracking, translation labels, and creation disclosure workflows.

The importer also maps high-signal Goodreads tags into coursework-friendly genres.

## Tech stack
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL for deployment or coursework submission
- SQLite fallback for local development and tests
- JWT with `python-jose`
- Pytest
- `python-dotenv` for `.env` loading

## Local setup on Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The application loads configuration automatically from `.env`, so database, auth, and documentation settings can be changed without editing source code.

Database schema changes are now managed with Alembic migrations rather than automatic table creation inside the application startup path.

API docs will be available at:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Import sample data
```powershell
.\.venv\Scripts\python.exe scripts\import_books.py scripts\sample_books.csv
```

## Import real public book data
Download and import directly:
```powershell
.\.venv\Scripts\python.exe scripts\import_books.py --download-goodbooks --goodbooks-dir scripts\goodbooks-10k --limit 1500 --min-ratings-count 10000 --reset
```

If the dataset has already been downloaded, you can reuse it:
```powershell
.\.venv\Scripts\python.exe scripts\import_books.py --goodbooks-dir scripts\goodbooks-10k --limit 1500 --min-ratings-count 10000
```

The importer protects against duplicate inserts by skipping books already present with the same `title`, `author`, and `source`.

## Run tests
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Database migrations
Create the current schema:
```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Create a new migration after model changes:
```powershell
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe change"
```

## Recommended demo flow
- Start the API and open Swagger at `/docs`
- Register and log in a user
- Import `goodbooks-10k` data
- Filter books with `source=goodbooks-10k`
- Create or update provenance metadata for one or two books with `PUT /books/{book_id}/provenance`
- Filter books by `origin_type`, `creation_disclosure`, or `moderation_status`
- Show `GET /books/{book_id}/similar` with `content_preference=human_only`
- Create reviews for a few books
- Show `/analytics/user-profile/{user_id}`
- Show provenance analytics such as `/analytics/creation-disclosure-distribution`
- Show `/analytics/recommendations/{user_id}` with `content_preference=human_only`
- Show metadata analytics such as `/analytics/language-distribution` and `/analytics/author-performance`

## Repository scope right now
This GitHub version is intentionally code-first while the final coursework deliverables are still being refined.

Included now:
- API source code
- Tests
- Import script and sample CSV data
- Setup instructions and environment template

To be added later for final coursework submission:
- API documentation PDF
- Technical report PDF
- Presentation slides
