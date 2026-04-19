from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from pydantic import ConfigDict

class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    published_year: Optional[int] = None
    average_rating: float = 0.0
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    average_rating: Optional[float] = None
    description: Optional[str] = None

class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
