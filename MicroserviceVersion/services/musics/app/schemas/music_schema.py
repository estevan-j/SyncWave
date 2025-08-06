from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MusicCreate(BaseModel):
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Artist identifier or code")
    album: Optional[str] = Field(None, description="Album name")
    url: Optional[str] = Field(None, description="Public audio file URL")
    cover_url: Optional[str] = Field(None, description="Cover image URL")
    artist_name: Optional[str] = Field(None, description="Artist's full name")
    artist_nickname: Optional[str] = Field(None, description="Artist's nickname")
    nationality: Optional[str] = Field(None, description="Artist's nationality code")

class MusicUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Song title")
    artist: Optional[str] = Field(None, description="Artist identifier or code")
    album: Optional[str] = Field(None, description="Album name")
    cover_url: Optional[str] = Field(None, description="Cover image URL")
    artist_name: Optional[str] = Field(None, description="Artist's full name")
    artist_nickname: Optional[str] = Field(None, description="Artist's nickname")
    nationality: Optional[str] = Field(None, description="Artist's nationality code")

class MusicResponse(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str]
    duration: Optional[int]
    url: Optional[str]
    cover_url: Optional[str]
    artist_name: Optional[str]
    artist_nickname: Optional[str]
    nationality: Optional[str]

    class Config:
        from_attributes = True
        populate_by_name = True