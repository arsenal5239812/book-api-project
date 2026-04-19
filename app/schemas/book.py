from datetime import datetime
from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    published_year: int | None = None
    average_rating: float = 0.0
    description: str | None = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    published_year: int | None = None
    average_rating: float | None = None
    description: str | None = None

class BookRead(BookBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True
