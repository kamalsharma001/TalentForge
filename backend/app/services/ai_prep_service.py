"""
AiPrepService — Candidate AI Interview Preparation & Conversational Mock Interview service.

Coordinates candidate context, strategic preparation plans, practice question generation,
real-time adaptive mock interview multi-turn dialogue, and comprehensive performance evaluations.
"""

import json
import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import io

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.interview import Interview
from app.models.mock_interview import MockInterview, MockInterviewStatus, MockInterviewMessage
from app.services.llm_service import LLMService
from app.services.cloudinary_service import CloudinaryService
from app.utils.errors import NotFoundError, ValidationError, ForbiddenError
from app.schemas.ai_prep_schema import (
    CandidateInterviewContextItem,
    PrepContextResponse,
    PrepPlanRequest,
    PrepPlanResponse,
    QuestionGenerateRequest,
    QuestionGenerateResponse,
    QuestionEvaluateRequest,
    QuestionEvaluateResponse,
    MockSessionStartRequest,
    MockSessionDetailResponse,
    MockMessageItem,
    MockMessageSendResponse,
    MockEvaluationResponse,
    CandidateResumeItem,
    ResumeUploadResponse,
)

logger = logging.getLogger(__name__)


class AiPrepService:

    @staticmethod
    def _get_or_create_candidate(db: Session, user_id: str) -> Candidate:
        candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not candidate:
            candidate = Candidate(user_id=user_id)
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
        return candidate

    # ── Resume Parsing & Intelligence ──────────────────────────────────────────
    @staticmethod
    def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
        """
        Extract raw text from PDF or DOCX binary stream.
        """
        lower = filename.lower()
        extracted_text = ""

        if lower.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                pages_text = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                extracted_text = "\n\n".join(pages_text).strip()
            except Exception as e:
                logger.error("Failed to extract PDF text from %s: %s", filename, e)
                raise ValidationError(f"Could not read PDF file: {str(e)}")

        elif lower.endswith(".docx") or lower.endswith(".doc"):
            try:
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                extracted_text = "\n".join(paragraphs).strip()
            except Exception as e:
                logger.error("Failed to extract DOCX text from %s: %s", filename, e)
                raise ValidationError(f"Could not read Word document: {str(e)}")

        elif lower.endswith(".txt"):
            try:
                extracted_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                extracted_text = file_bytes.decode("latin-1", errors="ignore")
        else:
            raise ValidationError("Unsupported file format. Please upload a PDF (.pdf) or Word document (.docx).")

        if len(extracted_text.strip()) < 30:
            raise ValidationError("The uploaded document contains insufficient text to analyze. Please ensure it is not scanned image-only.")

        return extracted_text

    @classmethod
    def upload_and_analyze_resume(
        cls,
        db: Session,
        user_id: str,
        file_bytes: bytes,
        filename: str,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extracts text, uploads raw file to storage, analyzes structured skills/claims with Gemini,
        and persists the resume record linked to the candidate.
        """
        candidate = cls._get_or_create_candidate(db, user_id)

        # 1. Extract text from file bytes
        extracted_text = cls.extract_text_from_file(file_bytes, filename)

        # 2. Upload to Cloudinary (gracefully falls back if offline or unconfigured)
        cloudinary_url = None
        cloudinary_id = None
        try:
            c_res = CloudinaryService.upload_resume(io.BytesIO(file_bytes), filename, str(candidate.id))
            cloudinary_url = c_res.get("url")
            cloudinary_id = c_res.get("cloudinary_id")
        except Exception as e:
            logger.warning("Cloudinary upload failed or offline (proceeding with local identifier): %s", e)
            cloudinary_url = f"/resumes/local/{filename}"
            cloudinary_id = f"local_{candidate.id}_{filename}"

        # 3. Analyze resume with Gemini
        analysis_data = LLMService.analyze_resume(extracted_text)

        # 4. Unset primary on other candidate resumes
        db.query(Resume).filter(Resume.candidate_id == candidate.id).update({"is_primary": False})

        # 5. Save resume entity
        resume = Resume(
            candidate_id=candidate.id,
            file_name=filename,
            cloudinary_url=cloudinary_url or "",
            cloudinary_id=cloudinary_id or "",
            file_size_bytes=len(file_bytes),
            mime_type=mime_type or "application/octet-stream",
            is_primary=True,
            extracted_text=extracted_text,
            parsed_data=json.dumps(analysis_data),
        )
        db.add(resume)

        # Sync skills to candidate profile if profile is unpopulated
        extracted_skills = []
        skills_obj = analysis_data.get("skills", {})
        if isinstance(skills_obj, dict):
            for v in skills_obj.values():
                if isinstance(v, list):
                    extracted_skills.extend(v)
        elif isinstance(skills_obj, list):
            extracted_skills = skills_obj

        if extracted_skills and (not candidate.skills or len(candidate.skills) < 3):
            merged = list(dict.fromkeys((candidate.skills or []) + extracted_skills))[:15]
            candidate.skills = merged

        db.commit()
        db.refresh(resume)

        return {
            "resume": {
                "id": resume.id,
                "candidate_id": resume.candidate_id,
                "file_name": resume.file_name,
                "file_size_bytes": resume.file_size_bytes,
                "mime_type": resume.mime_type,
                "cloudinary_url": resume.cloudinary_url,
                "is_primary": resume.is_primary,
                "uploaded_at": resume.uploaded_at,
                "parsed_data": analysis_data,
            },
            "analysis": analysis_data,
            "message": "Resume uploaded and analyzed successfully with Gemini.",
        }

    @classmethod
    def list_candidate_resumes(cls, db: Session, user_id: str) -> List[Dict[str, Any]]:
        candidate = cls._get_or_create_candidate(db, user_id)
        resumes = (
            db.query(Resume)
            .filter(Resume.candidate_id == candidate.id)
            .order_by(desc(Resume.uploaded_at))
            .all()
        )
        output = []
        for r in resumes:
            parsed = None
            if r.parsed_data:
                try:
                    parsed = json.loads(r.parsed_data)
                except Exception:
                    parsed = None
            output.append({
                "id": r.id,
                "candidate_id": r.candidate_id,
                "file_name": r.file_name,
                "file_size_bytes": r.file_size_bytes,
                "mime_type": r.mime_type,
                "cloudinary_url": r.cloudinary_url,
                "is_primary": r.is_primary,
                "uploaded_at": r.uploaded_at,
                "parsed_data": parsed,
            })
        return output

    @classmethod
    def get_candidate_context(cls, db: Session, user_id: str) -> PrepContextResponse:
        """
        Fetch candidate's upcoming and scheduled interviews along with candidate skills
        to hydrate the prep hub interface.
        """
        candidate = cls._get_or_create_candidate(db, user_id)

        # Retrieve candidate interviews ordered by scheduled_at or created_at
        interviews = (
            db.query(Interview)
            .filter(Interview.candidate_id == candidate.id)
            .order_by(desc(Interview.created_at))
            .all()
        )

        interview_items = [
            CandidateInterviewContextItem(
                id=inv.id,
                title=inv.title,
                job_role=inv.job_role,
                tech_stack=inv.tech_stack or [],
                difficulty=inv.difficulty or "medium",
                duration_mins=inv.duration_mins or 60,
                scheduled_at=inv.scheduled_at,
                status=inv.status.value if hasattr(inv.status, "value") else str(inv.status),
            )
            for inv in interviews
        ]

        return PrepContextResponse(
            interviews=interview_items,
            candidate_skills=candidate.skills or [],
            current_title=candidate.current_title,
            years_of_exp=candidate.years_of_exp,
        )

    @classmethod
    def generate_plan(cls, db: Session, user_id: str, data: PrepPlanRequest) -> PrepPlanResponse:
        """
        Generate strategic prep plan. If interview_id is provided, inherit role and tech stack.
        """
        candidate = cls._get_or_create_candidate(db, user_id)

        job_role = data.job_role
        tech_stack = data.tech_stack or []
        difficulty = data.difficulty

        if data.interview_id:
            interview = (
                db.query(Interview)
                .filter(Interview.id == data.interview_id, Interview.candidate_id == candidate.id)
                .first()
            )
            if interview:
                job_role = interview.job_role or job_role or interview.title
                tech_stack = interview.tech_stack or tech_stack
                difficulty = interview.difficulty or difficulty

        if not job_role:
            job_role = "Software Engineer"

        plan_dict = LLMService.generate_prep_plan(
            role=job_role,
            tech_stack=tech_stack,
            difficulty=difficulty,
            candidate_skills=candidate.skills or [],
        )

        return PrepPlanResponse(**plan_dict)

    @classmethod
    def generate_questions(cls, db: Session, user_id: str, data: QuestionGenerateRequest) -> QuestionGenerateResponse:
        """
        Generate role-specific practice questions.
        """
        candidate = cls._get_or_create_candidate(db, user_id)

        job_role = data.job_role
        tech_stack = data.tech_stack or []
        difficulty = data.difficulty

        if data.interview_id:
            interview = (
                db.query(Interview)
                .filter(Interview.id == data.interview_id, Interview.candidate_id == candidate.id)
                .first()
            )
            if interview:
                job_role = interview.job_role or job_role or interview.title
                tech_stack = interview.tech_stack or tech_stack
                difficulty = interview.difficulty or difficulty

        questions = LLMService.generate_practice_questions(
            role=job_role,
            tech_stack=tech_stack,
            difficulty=difficulty,
            category=data.category,
            count=data.count,
        )

        return QuestionGenerateResponse(questions=questions)

    @classmethod
    def evaluate_answer(cls, data: QuestionEvaluateRequest) -> QuestionEvaluateResponse:
        """
        Evaluate an individual candidate practice answer.
        """
        result = LLMService.evaluate_practice_answer(
            question=data.question,
            answer=data.answer,
            role=data.job_role,
            difficulty=data.difficulty,
        )
        return QuestionEvaluateResponse(**result)

    @classmethod
    def start_mock_session(cls, db: Session, user_id: str, data: MockSessionStartRequest) -> MockSessionDetailResponse:
        """
        Initialize a new conversational mock interview session:
        1. Generates an authoritative Interview Blueprint before Question 1.
        2. Initializes live competency tracking and claims validation states.
        3. Generates the opening question grounded in blueprint and candidate resume.
        4. Initializes server-side timer with duration mode.
        """
        candidate = cls._get_or_create_candidate(db, user_id)

        job_role = data.job_role
        tech_stack = data.tech_stack or []
        difficulty = data.difficulty

        if data.interview_id:
            interview = (
                db.query(Interview)
                .filter(Interview.id == data.interview_id, Interview.candidate_id == candidate.id)
                .first()
            )
            if interview:
                job_role = interview.job_role or job_role or interview.title
                tech_stack = interview.tech_stack or tech_stack
                difficulty = interview.difficulty or difficulty

        # Duration mode normalization
        duration_mode = str(data.duration_mode) if data.duration_mode else "30"
        if duration_mode == "open_ended":
            duration_mins = 0
        else:
            try:
                duration_mins = int(duration_mode)
            except ValueError:
                duration_mins = data.duration_mins or 30

        # Handle optional resume context
        resume_analysis = None
        resume_snapshot = None
        resume_id = data.resume_id

        if resume_id:
            resume = (
                db.query(Resume)
                .filter(Resume.id == resume_id, Resume.candidate_id == candidate.id)
                .first()
            )
            if resume and resume.parsed_data:
                try:
                    resume_analysis = json.loads(resume.parsed_data)
                    # Snapshot the parsed resume data so the session is immutable
                    resume_snapshot = resume.parsed_data
                except Exception as e:
                    logger.warning("Failed to parse resume snapshot: %s", e)

        # 1. Generate Interview Blueprint
        blueprint = LLMService.generate_interview_blueprint(
            role=job_role,
            tech_stack=tech_stack,
            difficulty=difficulty,
            duration_mode=duration_mode,
            resume_analysis=resume_analysis,
        )

        # 2. Initialize live competency tracking state
        live_competency_state = {}
        for comp in blueprint.get("competencies", []):
            cid = comp.get("id") or comp.get("name")
            live_competency_state[cid] = {
                "id": cid,
                "name": comp.get("name"),
                "priority": comp.get("priority", "medium"),
                "is_mandatory": comp.get("is_mandatory", False),
                "target_questions": comp.get("target_questions", 1),
                "expected_depth": comp.get("expected_depth", ""),
                "status": "not_started",
                "questions_asked": 0,
                "performance": "unassessed",
                "evidence": [],
                "consecutive_turns": 0,
                "is_current": False,
            }

        # 3. Initialize live claims state
        live_claims_state = []
        for claim_item in blueprint.get("claims_to_validate", []):
            live_claims_state.append({
                "claim": claim_item.get("claim"),
                "status": claim_item.get("status", "Requires further validation"),
                "evidence": "",
                "notes": "Pending live verification"
            })

        # 4. Generate Opening Question grounded in blueprint
        opener_result = LLMService.generate_mock_opener(
            role=job_role,
            tech_stack=tech_stack,
            difficulty=difficulty,
            interview_type=data.category,
            resume_analysis=resume_analysis,
            blueprint=blueprint,
        )
        opening_text = opener_result.get("content", "Hello! Let's begin our technical interview.")
        tested_comp = opener_result.get("tested_competency")

        # Update first competency state
        if tested_comp:
            for cid, cdata in live_competency_state.items():
                if cdata["name"].lower() == tested_comp.lower() or cid == "comp_1":
                    cdata["status"] = "in_progress"
                    cdata["questions_asked"] = 1
                    cdata["consecutive_turns"] = 1
                    cdata["is_current"] = True
                    break

        now_utc = datetime.now(timezone.utc)
        session = MockInterview(
            candidate_id=candidate.id,
            interview_id=data.interview_id,
            resume_id=resume_id,
            resume_snapshot=resume_snapshot,
            job_role=job_role,
            tech_stack=tech_stack,
            difficulty=difficulty,
            category=data.category,
            question_text=opening_text,
            duration_mins=duration_mins,
            duration_mode=duration_mode,
            started_at=now_utc,
            blueprint=json.dumps(blueprint),
            live_competency_state=json.dumps(live_competency_state),
            live_claims_state=json.dumps(live_claims_state),
            status=MockInterviewStatus.in_progress,
        )
        db.add(session)
        db.flush()

        # Insert opening message (sequence 1)
        first_message = MockInterviewMessage(
            mock_interview_id=session.id,
            role="interviewer",
            content=opening_text,
            sequence=1,
        )
        db.add(first_message)
        db.commit()
        db.refresh(session)

        # Remaining time
        rem_secs = (duration_mins * 60) if duration_mode != "open_ended" else None

        return MockSessionDetailResponse(
            id=session.id,
            candidate_id=session.candidate_id,
            interview_id=session.interview_id,
            resume_id=session.resume_id,
            job_role=session.job_role,
            tech_stack=session.tech_stack,
            difficulty=session.difficulty,
            category=session.category,
            status=session.status.value if hasattr(session.status, "value") else str(session.status),
            duration_mins=session.duration_mins,
            duration_mode=session.duration_mode,
            started_at=session.started_at,
            actual_duration_secs=session.actual_duration_secs,
            completion_reason=session.completion_reason,
            time_remaining_secs=rem_secs,
            time_elapsed_secs=0,
            resume_snapshot=session.resume_snapshot,
            blueprint=session.blueprint,
            live_competency_state=session.live_competency_state,
            live_claims_state=session.live_claims_state,
            competency_coverage=session.competency_coverage,
            validated_claims=session.validated_claims,
            ai_score=session.ai_score,
            ai_summary=session.ai_summary,
            ai_strengths=session.ai_strengths,
            ai_weaknesses=session.ai_weaknesses,
            evaluation_rubric=session.evaluation_rubric,
            recommendations=session.recommendations,
            messages=[MockMessageItem.model_validate(first_message)],
            created_at=session.created_at,
            completed_at=session.completed_at,
        )

    @classmethod
    def get_mock_session(cls, db: Session, user_id: str, session_id: UUID) -> MockSessionDetailResponse:
        """
        Get full details of a mock interview session including chronological transcript
        and live server-calculated time remaining.
        """
        candidate = cls._get_or_create_candidate(db, user_id)
        session = (
            db.query(MockInterview)
            .filter(MockInterview.id == session_id, MockInterview.candidate_id == candidate.id)
            .first()
        )
        if not session:
            raise NotFoundError("Mock interview session not found.")

        messages = (
            db.query(MockInterviewMessage)
            .filter(MockInterviewMessage.mock_interview_id == session.id)
            .order_by(MockInterviewMessage.sequence.asc())
            .all()
        )

        now = datetime.now(timezone.utc)
        started = session.started_at or session.created_at
        duration_mode = session.duration_mode or "30"

        if session.status == MockInterviewStatus.completed:
            # Completed session: lock duration and elapsed time
            actual_duration = session.actual_duration_secs or 0
            rem_secs = 0 if duration_mode != "open_ended" else None
            elapsed_secs = actual_duration
        else:
            elapsed_secs = int((now - started).total_seconds()) if started else 0
            rem_secs = None
            if duration_mode != "open_ended" and session.duration_mins:
                total_secs = session.duration_mins * 60
                rem_secs = max(0, total_secs - elapsed_secs)
                if rem_secs <= 0:
                    rem_secs = 0
                    elapsed_secs = total_secs
                    if not session.completion_reason:
                        session.completion_reason = "time_limit_reached"
                    if not session.actual_duration_secs:
                        session.actual_duration_secs = total_secs
                    if not session.completed_at and started:
                        session.completed_at = started + timedelta(seconds=total_secs)
                    db.commit()
            actual_duration = session.actual_duration_secs

        return MockSessionDetailResponse(
            id=session.id,
            candidate_id=session.candidate_id,
            interview_id=session.interview_id,
            resume_id=session.resume_id,
            job_role=session.job_role,
            tech_stack=session.tech_stack,
            difficulty=session.difficulty,
            category=session.category,
            status=session.status.value if hasattr(session.status, "value") else str(session.status),
            duration_mins=session.duration_mins or 30,
            duration_mode=session.duration_mode,
            started_at=session.started_at,
            actual_duration_secs=actual_duration,
            completion_reason=session.completion_reason,
            time_remaining_secs=rem_secs,
            time_elapsed_secs=elapsed_secs,
            resume_snapshot=session.resume_snapshot,
            blueprint=session.blueprint,
            live_competency_state=session.live_competency_state,
            live_claims_state=session.live_claims_state,
            competency_coverage=session.competency_coverage,
            validated_claims=session.validated_claims,
            ai_score=session.ai_score,
            ai_summary=session.ai_summary,
            ai_strengths=session.ai_strengths,
            ai_weaknesses=session.ai_weaknesses,
            evaluation_rubric=session.evaluation_rubric,
            recommendations=session.recommendations,
            messages=[MockMessageItem.model_validate(m) for m in messages],
            created_at=session.created_at,
            completed_at=session.completed_at,
        )

    @classmethod
    def send_mock_message(cls, db: Session, user_id: str, session_id: UUID, message_text: str) -> MockMessageSendResponse:
        """
        Candidate responds in the mock interview:
        - Server-side time tracking enforces pacing and graceful wrap-up when time expires.
        - Enforces interview blueprint adherence and topic rotation (max 2 consecutive turns).
        - Probes resume claims with increasing depth and distinguishes hands-on from hypothetical knowledge.
        - Prevents asking semantically duplicate questions.
        """
        candidate = cls._get_or_create_candidate(db, user_id)
        session = (
            db.query(MockInterview)
            .filter(MockInterview.id == session_id, MockInterview.candidate_id == candidate.id)
            .first()
        )
        if not session:
            raise NotFoundError("Mock interview session not found.")

        if session.status == MockInterviewStatus.completed:
            raise ValidationError("This mock interview session is already completed.")

        if session.completion_reason == "time_limit_reached":
            raise ValidationError("This mock interview session has ended because the time limit was reached.")

        # Calculate server-side time context before accepting candidate message
        now = datetime.now(timezone.utc)
        started = session.started_at or session.created_at
        elapsed_secs = int((now - started).total_seconds()) if started else 0
        duration_mode = session.duration_mode or "30"

        if duration_mode != "open_ended" and session.duration_mins:
            total_secs = session.duration_mins * 60
            if elapsed_secs >= total_secs:
                session.completion_reason = "time_limit_reached"
                session.actual_duration_secs = total_secs
                if not session.completed_at and started:
                    session.completed_at = started + timedelta(seconds=total_secs)
                db.commit()
                raise ValidationError("This mock interview session has ended because the allotted time has expired.")

        # Get existing message history
        existing_messages = (
            db.query(MockInterviewMessage)
            .filter(MockInterviewMessage.mock_interview_id == session.id)
            .order_by(MockInterviewMessage.sequence.asc())
            .all()
        )

        candidate_seq = len(existing_messages) + 1
        candidate_msg = MockInterviewMessage(
            mock_interview_id=session.id,
            role="candidate",
            content=message_text,
            sequence=candidate_seq,
        )
        db.add(candidate_msg)
        db.flush()

        # Build transcript for adaptive follow-up
        conversation_history = [
            {"role": m.role, "content": m.content}
            for m in existing_messages
        ]
        conversation_history.append({"role": "candidate", "content": message_text})

        is_closing_phase = False
        is_time_up = False
        remaining_secs = None

        if duration_mode != "open_ended" and session.duration_mins:
            total_secs = session.duration_mins * 60
            remaining_secs = max(0, total_secs - elapsed_secs)
            is_closing_phase = (remaining_secs <= int(total_secs * 0.25)) or (remaining_secs <= 180)
            is_time_up = (remaining_secs <= 60)

        time_context = {
            "duration_mode": duration_mode,
            "elapsed_secs": elapsed_secs,
            "remaining_secs": remaining_secs,
            "is_closing_phase": is_closing_phase,
            "is_time_up": is_time_up,
        }

        # Recent questions to avoid duplicates
        recent_questions = [m.content for m in existing_messages if m.role == "interviewer"]

        # Load session resume snapshot, blueprint, live states
        resume_analysis = None
        if session.resume_snapshot:
            try:
                resume_analysis = json.loads(session.resume_snapshot)
            except Exception:
                resume_analysis = None

        blueprint = None
        if session.blueprint:
            try:
                blueprint = json.loads(session.blueprint)
            except Exception:
                blueprint = None

        live_comp_state = {}
        if session.live_competency_state:
            try:
                live_comp_state = json.loads(session.live_competency_state)
            except Exception:
                live_comp_state = {}

        live_claims_state = []
        if session.live_claims_state:
            try:
                live_claims_state = json.loads(session.live_claims_state)
            except Exception:
                live_claims_state = []

        # Generate adaptive follow-up
        follow_up_result = LLMService.generate_mock_follow_up(
            role=session.job_role or "Software Engineer",
            tech_stack=session.tech_stack or [],
            difficulty=session.difficulty or "medium",
            conversation_history=conversation_history,
            resume_analysis=resume_analysis,
            blueprint=blueprint,
            live_competency_state=live_comp_state,
            live_claims_state=live_claims_state,
            time_context=time_context,
            recent_questions=recent_questions,
        )
        ai_content = follow_up_result.get("content", "Thank you for explaining. Let's move on to the next part.")
        tested_comp = follow_up_result.get("tested_competency")
        comp_rating = follow_up_result.get("competency_rating", "Adequate")
        evidence_snippet = follow_up_result.get("evidence_snippet", "")
        tested_claim = follow_up_result.get("tested_claim")
        claim_status = follow_up_result.get("claim_status")
        is_concluding = bool(follow_up_result.get("is_concluding") or is_time_up)

        # Update live competency state
        if tested_comp and live_comp_state:
            matched_key = None
            for cid, cdata in live_comp_state.items():
                if cdata.get("name", "").lower() == tested_comp.lower():
                    matched_key = cid
                    break
            if not matched_key:
                matched_key = f"comp_{len(live_comp_state)+1}"
                live_comp_state[matched_key] = {
                    "id": matched_key,
                    "name": tested_comp,
                    "status": "in_progress",
                    "questions_asked": 0,
                    "performance": "unassessed",
                    "evidence": [],
                    "consecutive_turns": 0,
                    "is_current": False,
                }

            # Update consecutive turns
            for cid, cdata in live_comp_state.items():
                if cid == matched_key:
                    if cdata.get("is_current"):
                        cdata["consecutive_turns"] = cdata.get("consecutive_turns", 1) + 1
                    else:
                        cdata["consecutive_turns"] = 1
                    cdata["is_current"] = True
                    cdata["questions_asked"] = cdata.get("questions_asked", 0) + 1
                    cdata["status"] = "covered" if cdata["questions_asked"] >= 2 else "in_progress"
                    cdata["performance"] = comp_rating
                    if evidence_snippet:
                        cdata.setdefault("evidence", []).append(evidence_snippet)
                else:
                    cdata["is_current"] = False
                    cdata["consecutive_turns"] = 0

            session.live_competency_state = json.dumps(live_comp_state)

        # Update live claims state
        if tested_claim and live_claims_state:
            for citem in live_claims_state:
                if citem.get("claim", "").lower() in tested_claim.lower() or tested_claim.lower() in citem.get("claim", "").lower():
                    if claim_status:
                        citem["status"] = claim_status
                    if evidence_snippet:
                        citem["evidence"] = evidence_snippet
                    citem["notes"] = f"Assessed during turn #{candidate_seq}: {comp_rating} performance."
            session.live_claims_state = json.dumps(live_claims_state)

        # Record completion reason if concluding
        if is_concluding:
            session.completion_reason = "time_limit_reached" if is_time_up else "natural"

        ai_seq = candidate_seq + 1
        ai_msg = MockInterviewMessage(
            mock_interview_id=session.id,
            role="interviewer",
            content=ai_content,
            sequence=ai_seq,
        )
        db.add(ai_msg)
        db.commit()
        db.refresh(candidate_msg)
        db.refresh(ai_msg)

        return MockMessageSendResponse(
            candidate_message=MockMessageItem.model_validate(candidate_msg),
            ai_response=MockMessageItem.model_validate(ai_msg),
            is_concluding=is_concluding,
            completion_reason=session.completion_reason,
        )

    @classmethod
    def end_mock_session(cls, db: Session, user_id: str, session_id: UUID, reason: Optional[str] = None) -> MockEvaluationResponse:
        """
        Conclude the mock interview:
        - Calculates actual elapsed duration server-side, strictly bounded by the configured duration mode.
        - Records explicit completion reason ('candidate_ended', 'time_limit_reached', 'natural').
        - Evaluates transcript with strict evidence grounding, 3-tier claim validation,
          and actionable next-step practice recommendations.
        """
        candidate = cls._get_or_create_candidate(db, user_id)
        session = (
            db.query(MockInterview)
            .filter(MockInterview.id == session_id, MockInterview.candidate_id == candidate.id)
            .first()
        )
        if not session:
            raise NotFoundError("Mock interview session not found.")

        # Check if already evaluated and completed
        if session.status == MockInterviewStatus.completed and session.ai_score is not None:
            try:
                rubric = json.loads(session.evaluation_rubric) if session.evaluation_rubric else {}
                hands_on = rubric.pop("_hands_on_vs_theoretical", None)
                strengths = json.loads(session.ai_strengths) if session.ai_strengths else []
                weaknesses = json.loads(session.ai_weaknesses) if session.ai_weaknesses else []
                recommendations = json.loads(session.recommendations) if session.recommendations else []
                coverage = json.loads(session.competency_coverage) if session.competency_coverage else None
                claims = json.loads(session.validated_claims) if session.validated_claims else None

                # Extract actionable recommendations if present in recommendations
                actionable = LLMService._default_actionable_recommendations(session.job_role, session.tech_stack)

                return MockEvaluationResponse(
                    session_id=session.id,
                    overall_score=session.ai_score or 0,
                    rubric=rubric,
                    summary=session.ai_summary or "Mock interview completed.",
                    strengths=strengths if isinstance(strengths, list) else [str(strengths)],
                    weaknesses=weaknesses if isinstance(weaknesses, list) else [str(weaknesses)],
                    recommendations=recommendations if isinstance(recommendations, list) else [str(recommendations)],
                    actionable_recommendations=actionable,
                    competency_coverage=coverage,
                    validated_claims=claims,
                    hands_on_vs_theoretical=hands_on,
                    duration_mode=session.duration_mode,
                    actual_duration_secs=session.actual_duration_secs,
                    completion_reason=session.completion_reason or "natural",
                    is_fallback=False,
                )
            except Exception as e:
                logger.warning("Error parsing stored evaluation JSON, will re-evaluate: %s", e)

        # Retrieve full conversation history
        messages = (
            db.query(MockInterviewMessage)
            .filter(MockInterviewMessage.mock_interview_id == session.id)
            .order_by(MockInterviewMessage.sequence.asc())
            .all()
        )

        conversation_history = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        # Calculate actual duration bounded by the allotted duration limit
        now = datetime.now(timezone.utc)
        started = session.started_at or session.created_at
        elapsed_secs = int((now - started).total_seconds()) if started else 0
        duration_mode = session.duration_mode or "30"

        if duration_mode != "open_ended" and session.duration_mins:
            total_secs = session.duration_mins * 60
            if session.completion_reason == "time_limit_reached" or reason == "time_limit_reached" or elapsed_secs >= total_secs:
                session.completion_reason = "time_limit_reached"
                actual_duration = total_secs
                completion_time = (started + timedelta(seconds=total_secs)) if started else now
            else:
                session.completion_reason = reason or session.completion_reason or "candidate_ended"
                actual_duration = min(elapsed_secs, total_secs)
                completion_time = now
        else:
            actual_duration = elapsed_secs
            session.completion_reason = reason or session.completion_reason or "candidate_ended"
            completion_time = now

        session.actual_duration_secs = actual_duration

        # Load session resume snapshot and blueprint
        resume_analysis = None
        if session.resume_snapshot:
            try:
                resume_analysis = json.loads(session.resume_snapshot)
            except Exception:
                resume_analysis = None

        blueprint = None
        if session.blueprint:
            try:
                blueprint = json.loads(session.blueprint)
            except Exception:
                blueprint = None

        live_comp_state = None
        if session.live_competency_state:
            try:
                live_comp_state = json.loads(session.live_competency_state)
            except Exception:
                live_comp_state = None

        # Call LLM evaluation
        eval_data = LLMService.evaluate_mock_session(
            role=session.job_role or "Software Engineer",
            tech_stack=session.tech_stack or [],
            difficulty=session.difficulty or "medium",
            conversation_history=conversation_history,
            resume_analysis=resume_analysis,
            blueprint=blueprint,
            live_competency_state=live_comp_state,
            duration_mode=session.duration_mode or "30",
            actual_duration_secs=actual_duration,
            completion_reason=session.completion_reason,
        )

        # Persist evaluation to session
        session.ai_score = eval_data.get("overall_score", 75)
        session.ai_summary = eval_data.get("summary", "")
        session.ai_strengths = json.dumps(eval_data.get("strengths", []))
        session.ai_weaknesses = json.dumps(eval_data.get("weaknesses", []))
        
        # Preserve hands_on_vs_theoretical inside evaluation rubric payload
        rubric_payload = dict(eval_data.get("rubric", {}))
        if eval_data.get("hands_on_vs_theoretical"):
            rubric_payload["_hands_on_vs_theoretical"] = eval_data.get("hands_on_vs_theoretical")
        session.evaluation_rubric = json.dumps(rubric_payload)

        session.recommendations = json.dumps(eval_data.get("recommendations", []))
        session.competency_coverage = json.dumps(eval_data.get("competency_coverage", {}))
        session.validated_claims = json.dumps(eval_data.get("validated_claims", []))
        session.status = MockInterviewStatus.completed
        session.completed_at = completion_time
        session.ai_generated_at = now

        db.commit()
        db.refresh(session)

        return MockEvaluationResponse(
            session_id=session.id,
            overall_score=eval_data.get("overall_score", 75),
            rubric=eval_data.get("rubric", {}),
            summary=eval_data.get("summary", ""),
            strengths=eval_data.get("strengths", []),
            weaknesses=eval_data.get("weaknesses", []),
            recommendations=eval_data.get("recommendations", []),
            actionable_recommendations=eval_data.get("actionable_recommendations", []),
            competency_coverage=eval_data.get("competency_coverage"),
            validated_claims=eval_data.get("validated_claims"),
            hands_on_vs_theoretical=eval_data.get("hands_on_vs_theoretical"),
            duration_mode=session.duration_mode,
            actual_duration_secs=session.actual_duration_secs,
            completion_reason=session.completion_reason,
            is_fallback=eval_data.get("is_fallback", False),
        )

    @classmethod
    def list_mock_sessions(cls, db: Session, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List previous AI mock interview sessions for the candidate.
        """
        candidate = cls._get_or_create_candidate(db, user_id)
        sessions = (
            db.query(MockInterview)
            .filter(MockInterview.candidate_id == candidate.id)
            .order_by(desc(MockInterview.created_at))
            .limit(limit)
            .all()
        )

        results = []
        for s in sessions:
            results.append({
                "id": str(s.id),
                "resume_id": str(s.resume_id) if s.resume_id else None,
                "job_role": s.job_role,
                "tech_stack": s.tech_stack,
                "difficulty": s.difficulty,
                "category": s.category,
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                "ai_score": s.ai_score,
                "duration_mins": s.duration_mins,
                "has_resume": bool(s.resume_snapshot or s.resume_id),
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            })
        return results

