from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


# ── Context Schemas ───────────────────────────────────────────────────────────

class CandidateInterviewContextItem(BaseModel):
    id: UUID
    title: str
    job_role: Optional[str] = None
    tech_stack: Optional[List[str]] = []
    difficulty: Optional[str] = "medium"
    duration_mins: Optional[int] = 60
    scheduled_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True


class PrepContextResponse(BaseModel):
    interviews: List[CandidateInterviewContextItem]
    candidate_skills: List[str] = []
    current_title: Optional[str] = None
    years_of_exp: Optional[int] = None


# ── Plan Schemas ──────────────────────────────────────────────────────────────

class PrepPlanRequest(BaseModel):
    interview_id: Optional[UUID] = None
    job_role: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    difficulty: str = "medium"


class FocusAreaItem(BaseModel):
    name: str
    description: str
    weight: str


class PrepPlanResponse(BaseModel):
    summary: str
    focus_areas: List[FocusAreaItem]
    recommended_topics: List[str]
    suggested_question_types: List[str]
    is_fallback: bool = False


# ── Question Generation Schemas ───────────────────────────────────────────────

class QuestionGenerateRequest(BaseModel):
    interview_id: Optional[UUID] = None
    job_role: str
    tech_stack: Optional[List[str]] = None
    difficulty: str = "medium"
    category: str = "technical"
    count: int = Field(5, ge=1, le=10)


class GeneratedQuestionItem(BaseModel):
    question: str
    category: str
    difficulty: str
    hint: Optional[str] = None
    evaluation_criteria: Optional[str] = None
    is_fallback: bool = False


class QuestionGenerateResponse(BaseModel):
    questions: List[GeneratedQuestionItem]


# ── Individual Practice Evaluation Schemas ────────────────────────────────────

class QuestionEvaluateRequest(BaseModel):
    question: str = Field(..., min_length=5)
    answer: str = Field(..., min_length=5)
    job_role: str = "Software Engineer"
    difficulty: str = "medium"


class QuestionEvaluateResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    score: int
    strengths: List[str]
    improvements: List[str]
    model_answer_snippet: Optional[str] = None
    summary: str
    is_fallback: bool = False


# ── Conversational Mock Interview Schemas ─────────────────────────────────────

class CandidateResumeItem(BaseModel):
    id: UUID
    candidate_id: UUID
    file_name: str
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    cloudinary_url: Optional[str] = None
    is_primary: bool
    uploaded_at: datetime
    parsed_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ResumeUploadResponse(BaseModel):
    resume: CandidateResumeItem
    analysis: Dict[str, Any]
    message: str


class MockSessionStartRequest(BaseModel):
    interview_id: Optional[UUID] = None
    resume_id: Optional[UUID] = None
    job_role: str
    tech_stack: Optional[List[str]] = None
    difficulty: str = "medium"
    category: str = "mixed"
    duration_mins: Optional[int] = Field(30, ge=0, le=120)
    duration_mode: str = "30"  # "15", "30", "45", "60", "open_ended"


class MockMessageItem(BaseModel):
    id: UUID
    role: str
    content: str
    sequence: int
    created_at: datetime

    class Config:
        from_attributes = True


class MockSessionDetailResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    interview_id: Optional[UUID] = None
    resume_id: Optional[UUID] = None
    job_role: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    difficulty: str
    category: str
    status: str
    duration_mins: int
    duration_mode: Optional[str] = "30"
    started_at: Optional[datetime] = None
    actual_duration_secs: Optional[int] = None
    completion_reason: Optional[str] = None
    time_remaining_secs: Optional[int] = None
    time_elapsed_secs: Optional[int] = None
    resume_snapshot: Optional[str] = None
    blueprint: Optional[str] = None
    live_competency_state: Optional[str] = None
    live_claims_state: Optional[str] = None
    competency_coverage: Optional[str] = None
    validated_claims: Optional[str] = None
    ai_score: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_strengths: Optional[str] = None
    ai_weaknesses: Optional[str] = None
    evaluation_rubric: Optional[str] = None
    recommendations: Optional[str] = None
    messages: List[MockMessageItem] = []
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MockMessageSendRequest(BaseModel):
    message: str = Field(..., min_length=1)


class MockMessageSendResponse(BaseModel):
    candidate_message: MockMessageItem
    ai_response: MockMessageItem
    is_concluding: bool = False
    completion_reason: Optional[str] = None


class MockEndRequest(BaseModel):
    reason: Optional[str] = None


class MockEvaluationResponse(BaseModel):
    session_id: UUID
    overall_score: int
    rubric: Dict[str, int]
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    actionable_recommendations: Optional[List[Dict[str, Any]]] = None
    competency_coverage: Optional[Dict[str, Any]] = None
    validated_claims: Optional[List[Dict[str, Any]]] = None
    hands_on_vs_theoretical: Optional[Any] = None
    duration_mode: Optional[str] = None
    actual_duration_secs: Optional[int] = None
    completion_reason: Optional[str] = None
    is_fallback: bool = False

