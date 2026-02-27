"""Data models for job scraping."""

from datetime import datetime
from pydantic import BaseModel, Field


class Job(BaseModel):
    """Represents a job posting from Avature."""
    
    job_id: str
    title: str
    company: str
    location: str = "Unknown"
    description: str = ""
    application_url: str
    date_posted: str | None = None
    category: str | None = None
    employment_type: str | None = None
    source_url: str = ""
    scraped_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        """Create job from dictionary."""
        return cls.model_validate(data)
