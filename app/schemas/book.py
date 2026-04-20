from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict

class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    genre: str = Field(min_length=1, max_length=100)
    published_year: Optional[int] = Field(default=None, ge=0, le=2100)
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    ratings_count: int = Field(default=0, ge=0)
    isbn13: Optional[str] = Field(default=None, max_length=20)
    language_code: Optional[str] = Field(default=None, max_length=10)
    source: str = Field(default="manual", min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    genre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    published_year: Optional[int] = Field(default=None, ge=0, le=2100)
    average_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    ratings_count: Optional[int] = Field(default=None, ge=0)
    isbn13: Optional[str] = Field(default=None, max_length=20)
    language_code: Optional[str] = Field(default=None, max_length=10)
    source: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)

class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
