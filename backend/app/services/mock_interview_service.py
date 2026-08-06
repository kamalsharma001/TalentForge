"""
MockInterviewService — handles mock interview session lifecycle.
Fully native FastAPI and legacy SQLAlchemy ORM service.
"""

import logging
import random
from sqlalchemy.orm import Session
from app.models.mock_interview import MockInterview, MockInterviewStatus
from app.models.practice_question import PracticeQuestion
from app.models.candidate import Candidate
from app.utils.errors import NotFoundError, ValidationError
from app.utils.pagination import paginate_query
from app.schemas.mock_interview_schema import MockInterviewResponse
from app.templates.mock_interview_templates import FALLBACK_QUESTIONS

logger = logging.getLogger(__name__)

class MockInterviewService:

    @staticmethod
    def create(db: Session, user_id: str, data: dict) -> dict:
        """Create a new mock interview session for the authenticated candidate."""
        candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not candidate:
            raise NotFoundError("Candidate profile not found.")

        job_role   = data.get("job_role")
        difficulty = data.get("difficulty", "medium")
        category   = data.get("category", "behavioral")
        duration   = data.get("duration_mins", 30)

        # Try to find a matching practice question
        query = db.query(PracticeQuestion).filter(
            PracticeQuestion.is_active == True,
            PracticeQuestion.difficulty == difficulty,
            PracticeQuestion.category == category,
        )
        if job_role:
            query = query.filter(PracticeQuestion.job_role.ilike(f"%{job_role}%"))

        questions = query.all()
        practice_question = random.choice(questions) if questions else None

        if practice_question:
            question_text = practice_question.question
            practice_question_id = practice_question.id
            job_role = job_role or practice_question.job_role
        else:
            fallback_list = FALLBACK_QUESTIONS.get(category, FALLBACK_QUESTIONS["behavioral"])
            question_text = random.choice(fallback_list)
            practice_question_id = None

        session = MockInterview(
            candidate_id=str(candidate.id),
            practice_question_id=practice_question_id,
            job_role=job_role,
            difficulty=difficulty,
            category=category,
            question_text=question_text,
            duration_mins=duration,
            status=MockInterviewStatus.in_progress,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return MockInterviewResponse.model_validate(session).model_dump()

    @staticmethod
    def list_for_candidate(db: Session, user_id: str, page: int = 1, per_page: int = 20) -> dict:
        """List mock interview sessions for the authenticated candidate."""
        candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not candidate:
            raise NotFoundError("Candidate profile not found.")

        query = (
            db.query(MockInterview)
            .filter(MockInterview.candidate_id == str(candidate.id))
            .order_by(MockInterview.created_at.desc())
        )

        res = paginate_query(query, page, per_page)
        # Serialize response items
        items_serialized = [MockInterviewResponse.model_validate(item).model_dump() for item in res["items"]]
        return {
            "items":    items_serialized,
            "total":    res["total"],
            "page":     res["page"],
            "pages":    res["pages"],
            "per_page": res["per_page"],
            "has_next": res["has_next"],
            "has_prev": res["has_prev"],
        }

    @staticmethod
    def get(db: Session, session_id: str, user_id: str) -> dict:
        """Get a single mock interview session."""
        session = db.query(MockInterview).get(session_id)
        if not session:
            raise NotFoundError("Mock interview session not found.")

        candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not candidate or str(session.candidate_id) != str(candidate.id):
            raise NotFoundError("Mock interview session not found.")

        return MockInterviewResponse.model_validate(session).model_dump()

    @staticmethod
    def submit_answer(db: Session, session_id: str, user_id: str, answer_text: str) -> dict:
        """Submit a candidate's answer for a mock interview session."""
        session = db.query(MockInterview).get(session_id)
        if not session:
            raise NotFoundError("Mock interview session not found.")

        candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not candidate or str(session.candidate_id) != str(candidate.id):
            raise NotFoundError("Mock interview session not found.")

        if session.status == MockInterviewStatus.completed:
            raise ValidationError("This session has already been completed.")

        session.answer_text = answer_text
        session.status = MockInterviewStatus.in_progress
        db.commit()
        db.refresh(session)

        return MockInterviewResponse.model_validate(session).model_dump()
