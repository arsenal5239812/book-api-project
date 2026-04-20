from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Review, User
from app.schemas.analytics import (
    BooksPerYearItem,
    GenreDistributionItem,
    MostReviewedBook,
    PreferredGenreItem,
    RecommendationResponse,
    RecentReviewItem,
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

@router.get("/recommendations/{user_id}", response_model=RecommendationResponse)
def recommendations(user_id: int, limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    preferred_genres = (
        db.query(Book.genre, func.avg(Review.rating).label("avg_rating"))
        .join(Review, Review.book_id == Book.id)
        .filter(Review.user_id == user_id)
        .group_by(Book.genre)
        .order_by(func.avg(Review.rating).desc())
        .all()
    )
    if not preferred_genres:
        return {
            "user_id": user_id,
            "preferred_genre": None,
            "rationale": "No reviews available yet, so personalised recommendations cannot be calculated.",
            "recommendations": [],
        }

    top_genre = preferred_genres[0][0]
    reviewed_book_ids = [book_id for (book_id,) in db.query(Review.book_id).filter(Review.user_id == user_id).all()]
    query = db.query(Book).filter(Book.genre == top_genre)
    if reviewed_book_ids:
        query = query.filter(~Book.id.in_(reviewed_book_ids))
    recs = query.order_by(Book.average_rating.desc(), Book.id.desc()).limit(limit).all()
    return {
        "user_id": user_id,
        "preferred_genre": top_genre,
        "rationale": f"Recommendations are based on the user's highest-rated genre: {top_genre}.",
        "recommendations": [
            {"id": b.id, "title": b.title, "average_rating": b.average_rating}
            for b in recs
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
