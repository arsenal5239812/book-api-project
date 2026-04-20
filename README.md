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
  - Search, sorting, and pagination on `GET /books`
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
  - User profile analytics
  - Explainable recommendations with ranking reasons

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

The importer also maps high-signal Goodreads tags into coursework-friendly genres.

## Tech stack
- FastAPI
- SQLAlchemy
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
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The application loads configuration automatically from `.env`, so database, auth, and documentation settings can be changed without editing source code.

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

## Recommended demo flow
- Start the API and open Swagger at `/docs`
- Register and log in a user
- Import `goodbooks-10k` data
- Filter books with `source=goodbooks-10k`
- Create reviews for a few books
- Show `/analytics/user-profile/{user_id}`
- Show `/analytics/recommendations/{user_id}`
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
