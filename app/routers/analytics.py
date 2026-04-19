from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Review, User

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/top-rated-books")
def top_rated_books(limit: int = 5, db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.average_rating.desc(), Book.id.desc()).limit(limit).all()
    return [{"id": b.id, "title": b.title, "average_rating": b.average_rating, "genre": b.genre} for b in books]

@router.get("/genre-distribution")
def genre_distribution(db: Session = Depends(get_db)):
    rows = db.query(Book.genre, func.count(Book.id)).group_by(Book.genre).all()
    return [{"genre": genre, "count": count} for genre, count in rows]

@router.get("/most-reviewed-books")
def most_reviewed_books(limit: int = 5, db: Session = Depends(get_db)):
    rows = (
        db.query(Book.id, Book.title, func.count(Review.id).label("review_count"))
        .outerjoin(Review, Review.book_id == Book.id)
        .group_by(Book.id)
        .order_by(func.count(Review.id).desc(), Book.id.desc())
        .limit(limit)
        .all()
    )
    return [{"id": row.id, "title": row.title, "review_count": row.review_count} for row in rows]

@router.get("/books-per-year")
def books_per_year(db: Session = Depends(get_db)):
    rows = db.query(Book.published_year, func.count(Book.id)).group_by(Book.published_year).order_by(Book.published_year).all()
    return [{"published_year": year, "count": count} for year, count in rows if year is not None]

@router.get("/recommendations/{user_id}")
def recommendations(user_id: int, limit: int = 5, db: Session = Depends(get_db)):
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
        return {"user_id": user_id, "recommendations": []}

    top_genre = preferred_genres[0][0]
    reviewed_book_ids = [book_id for (book_id,) in db.query(Review.book_id).filter(Review.user_id == user_id).all()]
    query = db.query(Book).filter(Book.genre == top_genre)
    if reviewed_book_ids:
        query = query.filter(~Book.id.in_(reviewed_book_ids))
    recs = query.order_by(Book.average_rating.desc(), Book.id.desc()).limit(limit).all()
    return {
        "user_id": user_id,
        "preferred_genre": top_genre,
        "recommendations": [
            {"id": b.id, "title": b.title, "average_rating": b.average_rating}
            for b in recs
        ],
    }
