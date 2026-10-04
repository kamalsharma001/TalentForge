from uuid import UUID
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import RoleChecker
from app.models.user import User
from app.schemas.ai_prep_schema import (
    PrepContextResponse,
    PrepPlanRequest,
    PrepPlanResponse,
    QuestionGenerateRequest,
    QuestionGenerateResponse,
    QuestionEvaluateRequest,
    QuestionEvaluateResponse,
    MockSessionStartRequest,
    MockSessionDetailResponse,
    MockMessageSendRequest,
    MockMessageSendResponse,
    MockEndRequest,
    MockEvaluationResponse,
    CandidateResumeItem,
    ResumeUploadResponse,
)
from app.services.ai_prep_service import AiPrepService
from app.utils.errors import ValidationError

router = APIRouter(prefix="/api/ai-prep", tags=["ai-prep"])


# ── Resume Ingestion & Intelligence Endpoints ─────────────────────────────────

@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Upload a candidate resume (PDF, DOCX, TXT) up to 5MB.
    Extracts text, stores asset, analyzes technical skills and verifiable claims with Gemini.
    """
    filename = file.filename or "resume.pdf"
    lower_name = filename.lower()
    if not (lower_name.endswith(".pdf") or lower_name.endswith(".docx") or lower_name.endswith(".doc") or lower_name.endswith(".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported document format. Please upload a PDF (.pdf) or Word document (.docx)."
        )

    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB limit. Please upload a smaller resume."
        )

    if len(file_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file appears to be empty or corrupted."
        )

    try:
        return AiPrepService.upload_and_analyze_resume(
            db=db,
            user_id=str(current_user.id),
            file_bytes=file_bytes,
            filename=filename,
            mime_type=file.content_type,
        )
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/resumes", response_model=List[CandidateResumeItem])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    List all uploaded resumes and structured analysis data for the authenticated candidate.
    """
    return AiPrepService.list_candidate_resumes(db, str(current_user.id))



@router.get("/context", response_model=PrepContextResponse)
def get_candidate_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Fetch candidate's scheduled interviews and profile skills for AI prep context.
    """
    return AiPrepService.get_candidate_context(db, str(current_user.id))


@router.post("/plan", response_model=PrepPlanResponse)
def generate_prep_plan(
    body: PrepPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Generate an AI-powered personalized study plan and strategic focus areas.
    """
    return AiPrepService.generate_plan(db, str(current_user.id), body)


@router.post("/questions/generate", response_model=QuestionGenerateResponse)
def generate_questions(
    body: QuestionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Generate realistic, role-specific technical/behavioral interview practice questions.
    """
    return AiPrepService.generate_questions(db, str(current_user.id), body)


@router.post("/questions/evaluate", response_model=QuestionEvaluateResponse)
def evaluate_question_answer(
    body: QuestionEvaluateRequest,
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Evaluate a candidate's individual answer to a practice question and provide actionable feedback.
    """
    return AiPrepService.evaluate_answer(body)


@router.post("/mock/start", response_model=MockSessionDetailResponse, status_code=status.HTTP_201_CREATED)
def start_mock_interview(
    body: MockSessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Start a live multi-turn AI mock interview session with an initial opening question.
    """
    return AiPrepService.start_mock_session(db, str(current_user.id), body)


@router.get("/mock/sessions")
def list_mock_sessions(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    List past and active mock interview sessions for the candidate.
    """
    return AiPrepService.list_mock_sessions(db, str(current_user.id), limit=limit)


@router.get("/mock/{session_id}", response_model=MockSessionDetailResponse)
def get_mock_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Get mock interview session details and full conversation history.
    """
    return AiPrepService.get_mock_session(db, str(current_user.id), session_id)


@router.post("/mock/{session_id}/message", response_model=MockMessageSendResponse)
def send_mock_message(
    session_id: UUID,
    body: MockMessageSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Submit a candidate response in the mock interview.
    The AI dynamically evaluates the answer and generates an adaptive follow-up question.
    """
    return AiPrepService.send_mock_message(db, str(current_user.id), session_id, body.message)


@router.post("/mock/{session_id}/end", response_model=MockEvaluationResponse)
def end_mock_interview(
    session_id: UUID,
    body: Optional[MockEndRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Conclude the mock interview and generate a multi-dimensional rubric score report.
    """
    reason = body.reason if body and body.reason else None
    return AiPrepService.end_mock_session(db, str(current_user.id), session_id, reason=reason)


@router.get("/mock/{session_id}/report", response_model=MockEvaluationResponse)
def get_mock_interview_report(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """
    Retrieve or finalize the evaluation report for a completed mock interview session.
    """
    return AiPrepService.end_mock_session(db, str(current_user.id), session_id)
