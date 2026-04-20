import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Book
from app.schemas.book import BookCreate, BookProvenanceUpdate, BookRead, BookUpdate, SimilarBookItem

router = APIRouter(prefix="/books", tags=["Books"])

@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
    description="Create a new book record with optional public-dataset metadata such as language code, ISBN13, and ratings count.",
)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    book = Book(**book_in.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.get(
    "",
    response_model=list[BookRead],
    summary="List books",
    description="Browse books with filtering, text search, sorting, and pagination. This endpoint supports both manual entries and imported public-dataset records.",
)
def list_books(
    genre: Optional[str] = Query(default=None, description="Filter by genre using a case-insensitive partial match."),
    author: Optional[str] = Query(default=None, description="Filter by author using a case-insensitive partial match."),
    language_code: Optional[str] = Query(default=None, min_length=1, max_length=10, description="Filter by language code such as 'eng'."),
    source: Optional[str] = Query(default=None, min_length=1, max_length=50, description="Filter by data source, for example 'manual' or 'goodbooks-10k'."),
    origin_type: Optional[str] = Query(default=None, description="Filter by origin type such as traditional_published, web_novel, or self_published."),
    source_platform: Optional[str] = Query(default=None, description="Filter by platform of origin such as goodreads, qidian, or fanqie."),
    translation_status: Optional[str] = Query(default=None, description="Filter by whether a work is original, translated, or unknown."),
    creation_disclosure: Optional[str] = Query(default=None, description="Filter by declared creation mode such as human_only or ai_assisted."),
    moderation_status: Optional[str] = Query(default=None, description="Filter by provenance moderation status such as verified or flagged."),
    search: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Search across title, author, genre, and description."),
    min_year: Optional[int] = Query(default=None, ge=0, le=2100, description="Only include books published on or after this year."),
    max_year: Optional[int] = Query(default=None, ge=0, le=2100, description="Only include books published on or before this year."),
    min_rating: Optional[float] = Query(default=None, ge=0.0, le=5.0, description="Only include books whose average rating meets this threshold."),
    min_ratings_count: Optional[int] = Query(default=None, ge=0, description="Only include books with at least this many community ratings."),
    max_ai_risk_score: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="Only include books whose AI risk score is at or below this threshold."),
    sort_by: str = Query(default="created_at", pattern="^(created_at|title|published_year|average_rating|ratings_count)$", description="Sort by creation time, title, publication year, average rating, or ratings count."),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort ascending or descending."),
    skip: int = Query(default=0, ge=0, description="Number of matching records to skip for pagination."),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return."),
    db: Session = Depends(get_db),
):
    query = db.query(Book)
    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if language_code:
        query = query.filter(Book.language_code.ilike(f"%{language_code}%"))
    if source:
        query = query.filter(Book.source.ilike(f"%{source}%"))
    if origin_type:
        query = query.filter(Book.origin_type == origin_type)
    if source_platform:
        query = query.filter(Book.source_platform == source_platform)
    if translation_status:
        query = query.filter(Book.translation_status == translation_status)
    if creation_disclosure:
        query = query.filter(Book.creation_disclosure == creation_disclosure)
    if moderation_status:
        query = query.filter(Book.moderation_status == moderation_status)
    if search:
        term = f"%{search}%"
        query = query.filter(
            Book.title.ilike(term) |
            Book.author.ilike(term) |
            Book.genre.ilike(term) |
            Book.description.ilike(term) |
            Book.provenance_notes.ilike(term)
        )
    if min_year is not None:
        query = query.filter(Book.published_year >= min_year)
    if max_year is not None:
        query = query.filter(Book.published_year <= max_year)
    if min_rating is not None:
        query = query.filter(Book.average_rating >= min_rating)
    if min_ratings_count is not None:
        query = query.filter(Book.ratings_count >= min_ratings_count)
    if max_ai_risk_score is not None:
        query = query.filter(Book.ai_risk_score.isnot(None), Book.ai_risk_score <= max_ai_risk_score)
    sort_column = getattr(Book, sort_by)
    if sort_order == "desc":
        sort_column = desc(sort_column)
    return query.order_by(sort_column, Book.id.desc()).offset(skip).limit(limit).all()

@router.get(
    "/{book_id}",
    response_model=BookRead,
    summary="Get a book",
    description="Retrieve a single book by its internal numeric identifier.",
)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get(
    "/{book_id}/similar",
    response_model=list[SimilarBookItem],
    summary="Find similar books",
    description="Discover books similar to a selected title using genre, language, publication era, provenance metadata, and content-preference-aware filtering.",
)
def similar_books(
    book_id: int,
    content_preference: str = Query(
        default="any",
        pattern="^(human_only|allow_ai_assisted|any)$",
        description="Filter similar titles by creation disclosure. Use human_only, allow_ai_assisted, or any.",
    ),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of similar books to return."),
    db: Session = Depends(get_db),
):
    anchor = db.query(Book).filter(Book.id == book_id).first()
    if not anchor:
        raise HTTPException(status_code=404, detail="Book not found")

    candidate_query = db.query(Book).filter(Book.id != book_id)
    if content_preference == "human_only":
        candidate_query = candidate_query.filter(Book.creation_disclosure == "human_only")
    elif content_preference == "allow_ai_assisted":
        candidate_query = candidate_query.filter(Book.creation_disclosure.in_(("human_only", "ai_assisted")))

    genre_candidates = candidate_query.filter(Book.genre == anchor.genre).all()
    if genre_candidates:
        candidates = genre_candidates
    else:
        candidates = candidate_query.limit(250).all()

    max_ratings_count = max((candidate.ratings_count for candidate in candidates), default=1)
    scored_candidates = []
    for candidate in candidates:
        score = 0.0
        reasons = []

        if candidate.genre == anchor.genre:
            score += 0.34
            reasons.append(f"Shares the same genre ({anchor.genre}).")
        elif anchor.genre != "General":
            score += 0.08

        if anchor.language_code and candidate.language_code == anchor.language_code:
            score += 0.12
            reasons.append(f"Matches the same language code ({anchor.language_code}).")

        if anchor.origin_type != "unknown" and candidate.origin_type == anchor.origin_type:
            score += 0.12
            reasons.append(f"Shares the same origin type ({anchor.origin_type}).")

        if anchor.translation_status != "unknown" and candidate.translation_status == anchor.translation_status:
            score += 0.08
            reasons.append(f"Shares the same translation status ({anchor.translation_status}).")

        if anchor.creation_disclosure != "unknown" and candidate.creation_disclosure == anchor.creation_disclosure:
            score += 0.08
            reasons.append(f"Shares the same creation disclosure ({anchor.creation_disclosure}).")

        if anchor.source_platform != "manual" and candidate.source_platform == anchor.source_platform:
            score += 0.07
            reasons.append(f"Comes from the same source platform ({anchor.source_platform}).")

        if anchor.original_language and candidate.original_language == anchor.original_language:
            score += 0.05
            reasons.append(f"Shares the same original language ({anchor.original_language}).")

        if anchor.published_year and candidate.published_year:
            year_distance = abs(candidate.published_year - anchor.published_year)
            year_score = max(0.0, 0.08 - min(year_distance / 100.0, 0.08))
            score += year_score
            if year_score >= 0.04:
                reasons.append("Published in a similar era.")

        popularity_score = (
            min(math.log1p(candidate.ratings_count) / math.log1p(max_ratings_count), 1.0) * 0.06
            if max_ratings_count
            else 0.0
        )
        score += popularity_score

        if candidate.moderation_status == "verified":
            score += 0.04
            reasons.append("Provenance metadata is verified.")

        if candidate.ai_risk_score is not None:
            score -= min(candidate.ai_risk_score * 0.05, 0.05)
            if candidate.ai_risk_score <= 0.1:
                reasons.append("Low AI risk score.")

        scored_candidates.append((round(score, 4), candidate, reasons[:4]))

    scored_candidates.sort(
        key=lambda item: (item[0], item[1].average_rating, item[1].ratings_count, item[1].id),
        reverse=True,
    )

    return [
        SimilarBookItem(
            **BookRead.model_validate(candidate).model_dump(),
            similarity_score=score,
            similarity_reasons=reasons or ["General metadata similarity match."],
        )
        for score, candidate, reasons in scored_candidates[:limit]
    ]

@router.put(
    "/{book_id}",
    response_model=BookRead,
    summary="Update a book",
    description="Update one or more fields on an existing book. Empty update payloads are rejected.",
)
def update_book(book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    update_data = book_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields supplied for update")
    for key, value in update_data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@router.put(
    "/{book_id}/provenance",
    response_model=BookRead,
    summary="Update book provenance",
    description="Update provenance and creation-disclosure metadata such as origin type, source platform, moderation status, and AI risk score.",
)
def update_book_provenance(book_id: int, provenance_in: BookProvenanceUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    update_data = provenance_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No provenance fields supplied for update")
    for key, value in update_data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description="Delete a book record by id. Returns 204 on success and 404 if the book does not exist.",
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
