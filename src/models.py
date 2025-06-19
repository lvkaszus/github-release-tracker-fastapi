from pydantic import BaseModel, validator
from datetime import datetime

class GitHubRelease(BaseModel):
    name: str
    tag_name: str
    published_at: str
    html_url: str

    @validator('name')
    def validate_name(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("name cannot be empty!")
        if len(v) > 32:
            raise ValueError("name must be less than 32 characters!")
        return v

    @validator('tag_name')
    def validate_tag_name(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("tag_name cannot be empty!")
        if len(v) > 32:
            raise ValueError("tag_name must be less than 32 characters!")
        return v

    @validator('published_at')
    def validate_published_date(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Incorrect published date format!")
        return v

    @validator('html_url')
    def validate_url(cls, v):
        if not v.startswith("https://github.com/"):
            raise ValueError("Incorrect GitHub HTML URL!")
        return v

class ReleaseResponse(BaseModel):
    name: str
    tag_name: str
    published_at: str
    html_url: str
