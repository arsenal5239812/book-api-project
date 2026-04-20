from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class TopRatedBook(BaseModel):
    id: int
    title: str
    average_rating: float
    genre: str


class GenreDistributionItem(BaseModel):
    genre: str
    count: int


class MostReviewedBook(BaseModel):
    id: int
    title: str
    review_count: int


class BooksPerYearItem(BaseModel):
    published_year: int
    count: int


class RecommendationItem(BaseModel):
    id: int
    title: str
    average_rating: float


class RecommendationResponse(BaseModel):
    user_id: int
    preferred_genre: Optional[str] = None
    rationale: str
    recommendations: list[RecommendationItem]


class PreferredGenreItem(BaseModel):
    genre: str
    average_rating_given: float


class RecentReviewItem(BaseModel):
    book_id: int
    book_title: str
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None


class UserProfileResponse(BaseModel):
    user_id: int
    review_count: int
    average_rating_given: float
    preferred_genres: list[PreferredGenreItem]
    recent_reviews: list[RecentReviewItem]
