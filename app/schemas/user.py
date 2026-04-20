from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from pydantic import ConfigDict

class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
