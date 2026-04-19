from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict

class ReviewBase(BaseModel):
    book_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: Optional[datetime] = None
