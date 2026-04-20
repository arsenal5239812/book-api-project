from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional
from pydantic import ConfigDict

OriginType = Literal["traditional_published", "web_novel", "self_published", "unknown"]
SourcePlatform = Literal["goodreads", "qidian", "fanqie", "manual", "other"]
TranslationStatus = Literal["original", "translated", "unknown"]
CreationDisclosure = Literal["human_only", "ai_assisted", "ai_generated", "unknown"]
DisclosureSource = Literal["author_declared", "platform_verified", "manual_admin", "system_flagged"]
ModerationStatus = Literal["unreviewed", "verified", "flagged", "disputed"]

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
    origin_type: OriginType = "unknown"
    source_platform: SourcePlatform = "manual"
    original_language: Optional[str] = Field(default=None, max_length=10)
    translation_status: TranslationStatus = "unknown"
    creation_disclosure: CreationDisclosure = "unknown"
    disclosure_source: Optional[DisclosureSource] = None
    moderation_status: ModerationStatus = "unreviewed"
    ai_risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    provenance_notes: Optional[str] = Field(default=None, max_length=2000)
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
    origin_type: Optional[OriginType] = None
    source_platform: Optional[SourcePlatform] = None
    original_language: Optional[str] = Field(default=None, max_length=10)
    translation_status: Optional[TranslationStatus] = None
    creation_disclosure: Optional[CreationDisclosure] = None
    disclosure_source: Optional[DisclosureSource] = None
    moderation_status: Optional[ModerationStatus] = None
    ai_risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    provenance_notes: Optional[str] = Field(default=None, max_length=2000)
    description: Optional[str] = Field(default=None, max_length=2000)


class BookProvenanceUpdate(BaseModel):
    origin_type: Optional[OriginType] = None
    source_platform: Optional[SourcePlatform] = None
    original_language: Optional[str] = Field(default=None, max_length=10)
    translation_status: Optional[TranslationStatus] = None
    creation_disclosure: Optional[CreationDisclosure] = None
    disclosure_source: Optional[DisclosureSource] = None
    moderation_status: Optional[ModerationStatus] = None
    ai_risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    provenance_notes: Optional[str] = Field(default=None, max_length=2000)

class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
