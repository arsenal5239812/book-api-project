from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Book
from app.schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    book = Book(**book_in.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.get("", response_model=list[BookRead])
def list_books(
    genre: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
    language_code: Optional[str] = Query(default=None, min_length=1, max_length=10),
    source: Optional[str] = Query(default=None, min_length=1, max_length=50),
    search: Optional[str] = Query(default=None, min_length=1, max_length=100),
    min_year: Optional[int] = Query(default=None, ge=0, le=2100),
    max_year: Optional[int] = Query(default=None, ge=0, le=2100),
    min_rating: Optional[float] = Query(default=None, ge=0.0, le=5.0),
    min_ratings_count: Optional[int] = Query(default=None, ge=0),
    sort_by: str = Query(default="created_at", pattern="^(created_at|title|published_year|average_rating)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
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
    if search:
        term = f"%{search}%"
        query = query.filter(
            Book.title.ilike(term) |
            Book.author.ilike(term) |
            Book.genre.ilike(term) |
            Book.description.ilike(term)
        )
    if min_year is not None:
        query = query.filter(Book.published_year >= min_year)
    if max_year is not None:
        query = query.filter(Book.published_year <= max_year)
    if min_rating is not None:
        query = query.filter(Book.average_rating >= min_rating)
    if min_ratings_count is not None:
        query = query.filter(Book.ratings_count >= min_ratings_count)
    sort_column = getattr(Book, sort_by)
    if sort_order == "desc":
        sort_column = desc(sort_column)
    return query.order_by(sort_column, Book.id.desc()).offset(skip).limit(limit).all()

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookRead)
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

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
