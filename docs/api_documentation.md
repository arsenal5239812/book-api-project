# API Documentation

## 1. Project
Book Metadata and Recommendation API

- Version: `1.0.0`
- Base URL (local): `http://127.0.0.1:8000`
- Interactive docs:
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - ReDoc: `http://127.0.0.1:8000/redoc`
  - OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## 2. Overview
This API provides:
- CRUD operations for books
- User registration and login with JWT bearer authentication
- Authenticated review creation and moderation rules
- Book analytics and user-profile analytics
- Explainable recommendations
- Provenance and AI-transparency metadata
- Provenance-aware similar-book discovery

The project also supports importing public book data from the `goodbooks-10k` dataset.

## 3. Authentication

### 3.1 Register
`POST /auth/register`

Request body:
```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "password": "secret123"
}
```

Successful response:
```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "id": 1,
  "created_at": "2026-04-21T10:00:00Z"
}
```

Common errors:
- `400 Bad Request` if the email is already registered
- `422 Unprocessable Entity` if validation fails

### 3.2 Login
`POST /auth/login`

Content type:
- `application/x-www-form-urlencoded`

Form fields:
- `username` = user email
- `password`

Example:
```text
username=alice@example.com
password=secret123
```

Successful response:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

Common errors:
- `401 Unauthorized` if credentials are invalid

### 3.3 Using the token
For protected endpoints, include:

```text
Authorization: Bearer <access_token>
```

Protected endpoints in this API include:
- `POST /reviews`
- `PUT /reviews/{review_id}`
- `DELETE /reviews/{review_id}`
- `GET /users/me`

## 4. Healthcheck

### 4.1 Root
`GET /`

Response:
```json
{
  "message": "Book Metadata and Recommendation API is running"
}
```

## 5. Books

### 5.1 Create book
`POST /books`

Request body example:
```json
{
  "title": "Deep Work",
  "author": "Cal Newport",
  "genre": "Productivity",
  "published_year": 2016,
  "average_rating": 4.2,
  "ratings_count": 50000,
  "isbn13": "9781455586691",
  "language_code": "eng",
  "source": "goodbooks-10k",
  "origin_type": "traditional_published",
  "source_platform": "goodreads",
  "original_language": "en",
  "translation_status": "original",
  "creation_disclosure": "human_only",
  "disclosure_source": "manual_admin",
  "moderation_status": "verified",
  "ai_risk_score": 0.02,
  "provenance_notes": "Imported public metadata with manually curated provenance labels.",
  "description": "Focus and concentration"
}
```

Successful response:
```json
{
  "id": 1,
  "title": "Deep Work",
  "author": "Cal Newport",
  "genre": "Productivity",
  "published_year": 2016,
  "average_rating": 4.2,
  "ratings_count": 50000,
  "isbn13": "9781455586691",
  "language_code": "eng",
  "source": "goodbooks-10k",
  "origin_type": "traditional_published",
  "source_platform": "goodreads",
  "original_language": "en",
  "translation_status": "original",
  "creation_disclosure": "human_only",
  "disclosure_source": "manual_admin",
  "moderation_status": "verified",
  "ai_risk_score": 0.02,
  "provenance_notes": "Imported public metadata with manually curated provenance labels.",
  "description": "Focus and concentration",
  "created_at": "2026-04-21T10:00:00Z"
}
```

### 5.2 List books
`GET /books`

Supported query parameters:
- `genre`
- `author`
- `language_code`
- `source`
- `origin_type`
- `source_platform`
- `translation_status`
- `creation_disclosure`
- `moderation_status`
- `search`
- `min_year`
- `max_year`
- `min_rating`
- `min_ratings_count`
- `max_ai_risk_score`
- `sort_by`
- `sort_order`
- `skip`
- `limit`

Example:
```text
GET /books?origin_type=web_novel&translation_status=translated&creation_disclosure=human_only&moderation_status=verified&max_ai_risk_score=0.10
```

Successful response example:
```json
[
  {
    "id": 4,
    "title": "Celestial Archive",
    "author": "Lin Yue",
    "genre": "Fantasy",
    "published_year": 2023,
    "average_rating": 4.4,
    "ratings_count": 0,
    "isbn13": null,
    "language_code": null,
    "source": "manual",
    "origin_type": "web_novel",
    "source_platform": "qidian",
    "original_language": "zh",
    "translation_status": "translated",
    "creation_disclosure": "human_only",
    "disclosure_source": "manual_admin",
    "moderation_status": "verified",
    "ai_risk_score": 0.08,
    "provenance_notes": "Translated Chinese web novel with manually curated provenance metadata.",
    "description": "Translated serial fantasy work",
    "created_at": "2026-04-21T10:05:00Z"
  }
]
```

### 5.3 Get book
`GET /books/{book_id}`

Successful response:
- returns one book object

Common errors:
- `404 Not Found` if the book does not exist

### 5.4 Update book
`PUT /books/{book_id}`

Request body example:
```json
{
  "genre": "Self-help",
  "average_rating": 4.5
}
```

Common errors:
- `400 Bad Request` if the request body is empty
- `404 Not Found` if the book does not exist

### 5.5 Update provenance
`PUT /books/{book_id}/provenance`

Purpose:
- update provenance, transparency, and moderation fields without changing the rest of the book record

Request body example:
```json
{
  "origin_type": "web_novel",
  "source_platform": "qidian",
  "original_language": "zh",
  "translation_status": "translated",
  "creation_disclosure": "human_only",
  "disclosure_source": "manual_admin",
  "moderation_status": "verified",
  "ai_risk_score": 0.08,
  "provenance_notes": "Translated Chinese web novel with manually curated provenance metadata."
}
```

Common errors:
- `400 Bad Request` if no provenance fields are supplied
- `404 Not Found` if the book does not exist

### 5.6 Similar-book discovery
`GET /books/{book_id}/similar`

Query parameters:
- `content_preference`
  - `human_only`
  - `allow_ai_assisted`
  - `any`
- `limit`

This endpoint uses:
- genre similarity
- language similarity
- origin type
- translation status
- creation disclosure
- source platform
- original language
- publication era
- ratings count
- moderation status
- AI risk score

Example:
```text
GET /books/4/similar?content_preference=human_only&limit=5
```

Successful response example:
```json
[
  {
    "id": 5,
    "title": "Star Scroll",
    "author": "Mei Dao",
    "genre": "Fantasy",
    "published_year": 2024,
    "average_rating": 4.7,
    "ratings_count": 18000,
    "isbn13": null,
    "language_code": "eng",
    "source": "manual",
    "origin_type": "web_novel",
    "source_platform": "qidian",
    "original_language": "zh",
    "translation_status": "translated",
    "creation_disclosure": "human_only",
    "disclosure_source": null,
    "moderation_status": "verified",
    "ai_risk_score": 0.02,
    "provenance_notes": "Strong similarity",
    "description": "Strong match",
    "created_at": "2026-04-21T10:07:00Z",
    "similarity_score": 0.86,
    "similarity_reasons": [
      "Shares the same genre (Fantasy).",
      "Matches the same language code (eng).",
      "Shares the same origin type (web_novel).",
      "Provenance metadata is verified."
    ]
  }
]
```

Common errors:
- `404 Not Found` if the anchor book does not exist

### 5.7 Delete book
`DELETE /books/{book_id}`

Successful response:
- `204 No Content`

Common errors:
- `404 Not Found`

## 6. Users

### 6.1 List users
`GET /users`

Response:
- array of user objects

### 6.2 Get current user
`GET /users/me`

Authentication:
- required

Successful response:
```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "id": 1,
  "created_at": "2026-04-21T10:00:00Z"
}
```

Common errors:
- `401 Unauthorized`

### 6.3 Get user by id
`GET /users/{user_id}`

Common errors:
- `404 Not Found`

## 7. Reviews

### 7.1 Create review
`POST /reviews`

Authentication:
- required

Request body example:
```json
{
  "book_id": 1,
  "rating": 5,
  "comment": "Excellent book"
}
```

Successful response:
```json
{
  "book_id": 1,
  "rating": 5,
  "comment": "Excellent book",
  "id": 1,
  "user_id": 1,
  "created_at": "2026-04-21T10:10:00Z"
}
```

Common errors:
- `401 Unauthorized`
- `404 Not Found` if the book does not exist
- `409 Conflict` if the same user already reviewed the same book

### 7.2 List reviews
`GET /reviews`

Query parameters:
- `book_id`
- `user_id`
- `min_rating`
- `skip`
- `limit`

### 7.3 Update review
`PUT /reviews/{review_id}`

Authentication:
- required

Request body example:
```json
{
  "rating": 4,
  "comment": "Updated review"
}
```

Common errors:
- `400 Bad Request` if the request body is empty
- `403 Forbidden` if the review belongs to another user
- `404 Not Found`

### 7.4 Delete review
`DELETE /reviews/{review_id}`

Authentication:
- required

Common errors:
- `403 Forbidden`
- `404 Not Found`

## 8. Analytics

### 8.1 Core analytics
- `GET /analytics/top-rated-books`
- `GET /analytics/genre-distribution`
- `GET /analytics/most-reviewed-books`
- `GET /analytics/books-per-year`
- `GET /analytics/language-distribution`
- `GET /analytics/source-distribution`
- `GET /analytics/rating-bands`
- `GET /analytics/author-performance`
- `GET /analytics/publication-decade-distribution`

Example response for `GET /analytics/top-rated-books`:
```json
[
  {
    "id": 3,
    "title": "Legend Falls",
    "average_rating": 4.8,
    "genre": "Fantasy"
  }
]
```

### 8.2 Provenance analytics
- `GET /analytics/creation-disclosure-distribution`
- `GET /analytics/moderation-status-distribution`
- `GET /analytics/web-novel-translation-distribution`

Example response:
```json
[
  { "creation_disclosure": "human_only", "count": 2 },
  { "creation_disclosure": "ai_assisted", "count": 1 }
]
```

### 8.3 User profile analytics
`GET /analytics/user-profile/{user_id}`

Successful response example:
```json
{
  "user_id": 1,
  "review_count": 2,
  "average_rating_given": 4.5,
  "preferred_genres": [
    {
      "genre": "Productivity",
      "average_rating_given": 4.5
    }
  ],
  "recent_reviews": [
    {
      "book_id": 1,
      "book_title": "Deep Work",
      "rating": 5,
      "comment": "Great",
      "created_at": "2026-04-21T10:10:00Z"
    }
  ]
}
```

Common errors:
- `404 Not Found`

### 8.4 Recommendation analytics
`GET /analytics/recommendations/{user_id}`

Query parameters:
- `content_preference`
  - `human_only`
  - `allow_ai_assisted`
  - `any`
- `limit`

This endpoint combines:
- user review history
- preferred genres
- language affinity
- community ratings
- popularity
- moderation status
- disclosure type
- AI risk score

Successful response example:
```json
{
  "user_id": 1,
  "content_preference_applied": "human_only",
  "preferred_genre": "Productivity",
  "preferred_language": "eng",
  "preference_summary": [
    {
      "genre": "Productivity",
      "average_rating_given": 4.5
    }
  ],
  "rationale": "Recommendations combine your highest-rated genres, overall book quality, reader popularity, language affinity, and provenance preferences to produce a ranked shortlist.",
  "recommendations": [
    {
      "id": 2,
      "title": "The Focus Formula",
      "average_rating": 4.7,
      "ratings_count": 80000,
      "genre": "Productivity",
      "language_code": "eng",
      "score": 0.82,
      "reasons": [
        "Matches your interest in Productivity.",
        "Matches your most-reviewed language (eng).",
        "Provenance metadata has been platform-verified."
      ]
    }
  ]
}
```

Common errors:
- `404 Not Found` if the user does not exist

Special case:
- if the user has not reviewed any books yet, the endpoint still returns `200 OK` with an empty recommendation list and an explanatory rationale

## 9. Common HTTP status codes
- `200 OK` successful read or update
- `201 Created` successful create
- `204 No Content` successful delete
- `400 Bad Request` invalid request for business rules
- `401 Unauthorized` missing or invalid authentication
- `403 Forbidden` authenticated but not allowed to edit/delete that resource
- `404 Not Found` resource does not exist
- `409 Conflict` duplicate review for the same user and book
- `422 Unprocessable Entity` schema validation failure

## 10. Local execution checklist
1. Install dependencies
2. Run database migrations
3. Start the API
4. Open Swagger UI
5. Register a user
6. Log in and authorize
7. Create books and provenance metadata
8. Create reviews
9. Test analytics, recommendations, and similar-book discovery

## 11. Suggested command sequence
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
