from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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


class LanguageDistributionItem(BaseModel):
    language_code: str
    count: int


class SourceDistributionItem(BaseModel):
    source: str
    count: int


class RatingBandItem(BaseModel):
    band: str
    count: int


class AuthorPerformanceItem(BaseModel):
    author: str
    book_count: int
    average_rating: float
    total_ratings_count: int


class PublicationDecadeItem(BaseModel):
    decade: str
    count: int


class CreationDisclosureDistributionItem(BaseModel):
    creation_disclosure: str
    count: int


class ModerationStatusDistributionItem(BaseModel):
    moderation_status: str
    count: int


class WebNovelTranslationDistributionItem(BaseModel):
    translation_status: str
    count: int


class PreferredGenreItem(BaseModel):
    genre: str
    average_rating_given: float


class RecommendationItem(BaseModel):
    id: int
    title: str
    average_rating: float
    ratings_count: int
    genre: str
    language_code: Optional[str] = None
    score: float
    reasons: list[str]


class RecommendationResponse(BaseModel):
    user_id: int
    content_preference_applied: str = "any"
    preferred_genre: Optional[str] = None
    preferred_language: Optional[str] = None
    preference_summary: list[PreferredGenreItem]
    rationale: str
    recommendations: list[RecommendationItem]


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
