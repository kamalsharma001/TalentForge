"""
MockInterviewService — handles mock interview session lifecycle.

Features:
1. Creates a new session with a question from the practice bank (or fallback)
2. Lists sessions for a candidate with pagination
3. Retrieves single session
4. Submits candidate answer and marks session in_progress
"""

import logging
import random

from app import db
from app.models.mock_interview import MockInterview, MockInterviewStatus
from app.models.practice_question import PracticeQuestion
from app.models.candidate import Candidate
from app.utils.errors import NotFoundError, ValidationError
from app.utils.pagination import paginate_query
from app.schemas.mock_interview_schema import MockInterviewSchema

from app.templates.mock_interview_templates import FALLBACK_QUESTIONS

logger = logging.getLogger(__name__)


class MockInterviewService:

    @staticmethod
    def create(user_id: str, data: dict) -> dict:
        """Create a new mock interview session for the authenticated candidate."""

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            raise NotFoundError("Candidate profile not found.")

        job_role   = data.get("job_role")
        difficulty = data.get("difficulty", "medium")
        category   = data.get("category", "behavioral")
        duration   = data.get("duration_mins", 30)

        # Try to find a matching practice question
        query = PracticeQuestion.query.filter_by(
            is_active=True,
            difficulty=difficulty,
            category=category,
        )
        if job_role:
            query = query.filter(PracticeQuestion.job_role.ilike(f"%{job_role}%"))

        questions = query.all()
        practice_question = random.choice(questions) if questions else None

        if practice_question:
            question_text = practice_question.question
            practice_question_id = practice_question.id
            # Use the practice question's job_role if candidate didn't specify
            job_role = job_role or practice_question.job_role
        else:
            # Fallback to template questions
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

        db.session.add(session)
        db.session.commit()

        return MockInterviewSchema().dump(session)

    @staticmethod
    def list_for_candidate(user_id: str, page: int = 1, per_page: int = 20) -> dict:
        """List mock interview sessions for the authenticated candidate."""

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            raise NotFoundError("Candidate profile not found.")

        query = (
            MockInterview.query
            .filter_by(candidate_id=str(candidate.id))
            .order_by(MockInterview.created_at.desc())
        )

        return paginate_query(query, page, per_page, MockInterviewSchema())

    @staticmethod
    def get(session_id: str, user_id: str) -> dict:
        """Get a single mock interview session."""

        session = MockInterview.query.get(session_id)
        if not session:
            raise NotFoundError("Mock interview session not found.")

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate or str(session.candidate_id) != str(candidate.id):
            raise NotFoundError("Mock interview session not found.")

        return MockInterviewSchema().dump(session)

    @staticmethod
    def submit_answer(session_id: str, user_id: str, answer_text: str) -> dict:
        """Submit a candidate's answer for a mock interview session."""

        session = MockInterview.query.get(session_id)
        if not session:
            raise NotFoundError("Mock interview session not found.")

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate or str(session.candidate_id) != str(candidate.id):
            raise NotFoundError("Mock interview session not found.")

        if session.status == MockInterviewStatus.completed:
            raise ValidationError("This session has already been completed.")

        session.answer_text = answer_text
        session.status = MockInterviewStatus.in_progress
        db.session.commit()

        return MockInterviewSchema().dump(session)
