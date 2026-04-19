from datetime import datetime
from pydantic import BaseModel, Field

class ReviewBase(BaseModel):
    book_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None

class ReviewRead(ReviewBase):
    id: int
    user_id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True
