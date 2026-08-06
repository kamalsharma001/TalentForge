from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class InterviewReportResponse(BaseModel):
    id: UUID
    interview_id: UUID
    summary: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: Optional[str] = None
    private_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_strengths: Optional[str] = None
    ai_weaknesses: Optional[str] = None
    ai_generated_at: Optional[datetime] = None
    decision: Optional[str] = None
    overall_score: Optional[Decimal] = None
    is_published: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReportCreateRequest(BaseModel):
    summary: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: Optional[str] = None
    private_notes: Optional[str] = None
    decision: Optional[str] = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v):
        if v is not None and v not in ("hire", "hold", "no_hire"):
            raise ValueError("decision must be hire, hold, or no_hire")
        return v

class ReportUpdateRequest(ReportCreateRequest):
    pass

class CandidateReportResponse(BaseModel):
    id: UUID
    interview_id: UUID
    summary: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: Optional[str] = None
    ai_summary: Optional[str] = None
    decision: Optional[str] = None
    overall_score: Optional[Decimal] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
