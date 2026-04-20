import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Review, User
from app.schemas.analytics import (
    AuthorPerformanceItem,
    BooksPerYearItem,
    GenreDistributionItem,
    LanguageDistributionItem,
    MostReviewedBook,
    PreferredGenreItem,
    PublicationDecadeItem,
    RatingBandItem,
    RecommendationResponse,
    RecentReviewItem,
    SourceDistributionItem,
    TopRatedBook,
    UserProfileResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/top-rated-books", response_model=list[TopRatedBook])
def top_rated_books(limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.average_rating.desc(), Book.id.desc()).limit(limit).all()
    return [{"id": b.id, "title": b.title, "average_rating": b.average_rating, "genre": b.genre} for b in books]


@router.get("/genre-distribution", response_model=list[GenreDistributionItem])
def genre_distribution(db: Session = Depends(get_db)):
    rows = db.query(Book.genre, func.count(Book.id)).group_by(Book.genre).all()
    return [{"genre": genre, "count": count} for genre, count in rows]


@router.get("/most-reviewed-books", response_model=list[MostReviewedBook])
def most_reviewed_books(limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    rows = (
        db.query(Book.id, Book.title, func.count(Review.id).label("review_count"))
        .outerjoin(Review, Review.book_id == Book.id)
        .group_by(Book.id)
        .order_by(func.count(Review.id).desc(), Book.id.desc())
        .limit(limit)
        .all()
    )
    return [{"id": row.id, "title": row.title, "review_count": row.review_count} for row in rows]


@router.get("/books-per-year", response_model=list[BooksPerYearItem])
def books_per_year(db: Session = Depends(get_db)):
    rows = db.query(Book.published_year, func.count(Book.id)).group_by(Book.published_year).order_by(Book.published_year).all()
    return [{"published_year": year, "count": count} for year, count in rows if year is not None]


@router.get("/language-distribution", response_model=list[LanguageDistributionItem])
def language_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(Book.language_code, func.count(Book.id))
        .filter(Book.language_code.isnot(None))
        .group_by(Book.language_code)
        .order_by(func.count(Book.id).desc(), Book.language_code.asc())
        .all()
    )
    return [{"language_code": language_code, "count": count} for language_code, count in rows]


@router.get("/source-distribution", response_model=list[SourceDistributionItem])
def source_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(Book.source, func.count(Book.id))
        .group_by(Book.source)
        .order_by(func.count(Book.id).desc(), Book.source.asc())
        .all()
    )
    return [{"source": source, "count": count} for source, count in rows]


@router.get("/rating-bands", response_model=list[RatingBandItem])
def rating_bands(db: Session = Depends(get_db)):
    bands = [
        ("below_3", db.query(func.count(Book.id)).filter(Book.average_rating < 3).scalar() or 0),
        ("3_to_4", db.query(func.count(Book.id)).filter(Book.average_rating >= 3, Book.average_rating < 4).scalar() or 0),
        ("4_to_4_5", db.query(func.count(Book.id)).filter(Book.average_rating >= 4, Book.average_rating < 4.5).scalar() or 0),
        ("4_5_and_above", db.query(func.count(Book.id)).filter(Book.average_rating >= 4.5).scalar() or 0),
    ]
    return [{"band": band, "count": int(count)} for band, count in bands]


@router.get("/author-performance", response_model=list[AuthorPerformanceItem])
def author_performance(limit: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    rows = (
        db.query(
            Book.author,
            func.count(Book.id).label("book_count"),
            func.avg(Book.average_rating).label("average_rating"),
            func.sum(Book.ratings_count).label("total_ratings_count"),
        )
        .group_by(Book.author)
        .having(func.count(Book.id) >= 1)
        .order_by(func.avg(Book.average_rating).desc(), func.sum(Book.ratings_count).desc(), Book.author.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "author": author,
            "book_count": int(book_count),
            "average_rating": round(float(average_rating or 0.0), 2),
            "total_ratings_count": int(total_ratings_count or 0),
        }
        for author, book_count, average_rating, total_ratings_count in rows
    ]


@router.get("/publication-decade-distribution", response_model=list[PublicationDecadeItem])
def publication_decade_distribution(db: Session = Depends(get_db)):
    rows = db.query(Book.published_year).filter(Book.published_year.isnot(None)).all()
    counts: dict[str, int] = {}
    for (published_year,) in rows:
        decade_start = (published_year // 10) * 10
        label = f"{decade_start}s"
        counts[label] = counts.get(label, 0) + 1
    return [{"decade": decade, "count": counts[decade]} for decade in sorted(counts.keys())]


@router.get("/recommendations/{user_id}", response_model=RecommendationResponse)
def recommendations(user_id: int, limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    preferred_genres = (
        db.query(Book.genre, func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("review_count"))
        .join(Review, Review.book_id == Book.id)
        .filter(Review.user_id == user_id)
        .group_by(Book.genre)
        .order_by(func.avg(Review.rating).desc(), func.count(Review.id).desc(), Book.genre.asc())
        .all()
    )
    if not preferred_genres:
        return {
            "user_id": user_id,
            "preferred_genre": None,
            "preferred_language": None,
            "preference_summary": [],
            "rationale": "No reviews available yet, so personalised recommendations cannot be calculated.",
            "recommendations": [],
        }

    reviewed_book_ids = [book_id for (book_id,) in db.query(Review.book_id).filter(Review.user_id == user_id).all()]
    preferred_language_row = (
        db.query(Book.language_code, func.count(Review.id).label("review_count"))
        .join(Review, Review.book_id == Book.id)
        .filter(Review.user_id == user_id, Book.language_code.isnot(None))
        .group_by(Book.language_code)
        .order_by(func.count(Review.id).desc(), Book.language_code.asc())
        .first()
    )
    preferred_language = preferred_language_row[0] if preferred_language_row else None
    preferred_year = (
        db.query(func.avg(Book.published_year))
        .join(Review, Review.book_id == Book.id)
        .filter(Review.user_id == user_id, Book.published_year.isnot(None))
        .scalar()
    )

    top_genre = preferred_genres[0][0]
    top_genres = [genre for genre, _, _ in preferred_genres[:3]]
    genre_scores = {
        genre: min(1.0, (float(avg_rating) / 5.0) * (1 + min(review_count, 3) * 0.15))
        for genre, avg_rating, review_count in preferred_genres
    }

    candidate_query = db.query(Book).filter(~Book.id.in_(reviewed_book_ids))
    if top_genres:
        candidate_query = candidate_query.filter(Book.genre.in_(top_genres))
    candidates = (
        candidate_query
        .order_by(Book.average_rating.desc(), Book.ratings_count.desc(), Book.id.desc())
        .limit(250)
        .all()
    )

    max_ratings_count = max((book.ratings_count for book in candidates), default=1)
    scored_recommendations = []
    for book in candidates:
        genre_component = genre_scores.get(book.genre, 0.35)
        rating_component = min(book.average_rating / 5.0, 1.0)
        popularity_component = (
            min(math.log1p(book.ratings_count) / math.log1p(max_ratings_count), 1.0)
            if max_ratings_count
            else 0.0
        )
        language_component = 0.12 if preferred_language and book.language_code == preferred_language else 0.0
        year_component = 0.0
        if preferred_year and book.published_year:
            distance = abs(book.published_year - preferred_year)
            year_component = max(0.0, 0.08 - min(distance / 100.0, 0.08))

        score = (
            genre_component * 0.4
            + rating_component * 0.3
            + popularity_component * 0.18
            + language_component
            + year_component
        )
        reasons = [f"Matches your interest in {book.genre}."]
        if preferred_language and book.language_code == preferred_language:
            reasons.append(f"Matches your most-reviewed language ({preferred_language}).")
        if book.average_rating >= 4.2:
            reasons.append(f"Strong community rating of {book.average_rating:.2f}.")
        if book.ratings_count >= 50000:
            reasons.append(f"Backed by high reader engagement ({book.ratings_count} ratings).")
        scored_recommendations.append((score, book, reasons[:3]))

    scored_recommendations.sort(
        key=lambda item: (item[0], item[1].average_rating, item[1].ratings_count, item[1].id),
        reverse=True,
    )
    top_recommendations = scored_recommendations[:limit]

    return {
        "user_id": user_id,
        "preferred_genre": top_genre,
        "preferred_language": preferred_language,
        "preference_summary": [
            PreferredGenreItem(genre=genre, average_rating_given=round(float(avg_rating), 2))
            for genre, avg_rating, _ in preferred_genres[:3]
        ],
        "rationale": (
            "Recommendations combine your highest-rated genres, overall book quality, reader popularity, "
            "and language affinity to produce a ranked shortlist."
        ),
        "recommendations": [
            {
                "id": book.id,
                "title": book.title,
                "average_rating": book.average_rating,
                "ratings_count": book.ratings_count,
                "genre": book.genre,
                "language_code": book.language_code,
                "score": round(score, 4),
                "reasons": reasons,
            }
            for score, book, reasons in top_recommendations
        ],
    }


@router.get("/user-profile/{user_id}", response_model=UserProfileResponse)
def user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    review_count = db.query(func.count(Review.id)).filter(Review.user_id == user_id).scalar() or 0
    average_rating_given = db.query(func.avg(Review.rating)).filter(Review.user_id == user_id).scalar() or 0.0
    preferred_genres = (
        db.query(Book.genre, func.avg(Review.rating).label("avg_rating"))
        .join(Review, Review.book_id == Book.id)
        .filter(Review.user_id == user_id)
        .group_by(Book.genre)
        .order_by(func.avg(Review.rating).desc(), Book.genre.asc())
        .limit(3)
        .all()
    )
    recent_reviews = (
        db.query(Review, Book.title)
        .join(Book, Book.id == Review.book_id)
        .filter(Review.user_id == user_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
        .limit(5)
        .all()
    )

    return {
        "user_id": user_id,
        "review_count": int(review_count),
        "average_rating_given": round(float(average_rating_given), 2),
        "preferred_genres": [
            PreferredGenreItem(genre=genre, average_rating_given=round(float(avg_rating), 2))
            for genre, avg_rating in preferred_genres
        ],
        "recent_reviews": [
            RecentReviewItem(
                book_id=review.book_id,
                book_title=book_title,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at,
            )
            for review, book_title in recent_reviews
        ],
    }
