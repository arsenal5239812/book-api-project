from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Book, Review, User
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(review_in: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == review_in.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    existing_review = (
        db.query(Review)
        .filter(Review.book_id == review_in.book_id, Review.user_id == current_user.id)
        .first()
    )
    if existing_review:
        raise HTTPException(status_code=409, detail="You have already reviewed this book")
    review = Review(user_id=current_user.id, **review_in.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    _refresh_book_average(db, review.book_id)
    return review

@router.get("", response_model=list[ReviewRead])
def list_reviews(
    book_id: Optional[int] = Query(default=None, ge=1),
    user_id: Optional[int] = Query(default=None, ge=1),
    min_rating: Optional[int] = Query(default=None, ge=1, le=5),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Review)
    if book_id is not None:
        query = query.filter(Review.book_id == book_id)
    if user_id is not None:
        query = query.filter(Review.user_id == user_id)
    if min_rating is not None:
        query = query.filter(Review.rating >= min_rating)
    return query.order_by(Review.id.desc()).offset(skip).limit(limit).all()

@router.put("/{review_id}", response_model=ReviewRead)
def update_review(review_id: int, review_in: ReviewUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own reviews")
    update_data = review_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields supplied for update")
    for key, value in update_data.items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    _refresh_book_average(db, review.book_id)
    return review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")
    book_id = review.book_id
    db.delete(review)
    db.commit()
    _refresh_book_average(db, book_id)


def _refresh_book_average(db: Session, book_id: int) -> None:
    average = db.query(func.avg(Review.rating)).filter(Review.book_id == book_id).scalar() or 0.0
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        book.average_rating = round(float(average), 2)
        db.commit()
