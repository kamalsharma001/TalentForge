import logging
import random
import time
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.interview import Interview
from app.models.mock_interview import MockInterview, MockInterviewStatus
from app.utils.errors import NotFoundError, ServiceUnavailableError, ValidationError

from app.templates.ai_feedback_templates import (
    HIGH_PERFORMANCE,
    MODERATE_PERFORMANCE,
    LOW_PERFORMANCE
)

from app.templates.mock_interview_templates import (
    HIGH_PERFORMANCE as MOCK_HIGH,
    MODERATE_PERFORMANCE as MOCK_MODERATE,
    LOW_PERFORMANCE as MOCK_LOW,
)

logger = logging.getLogger(__name__)

class AiFeedbackService:

    @staticmethod
    def generate(db: Session, interview_id: str) -> dict:
        interview = db.get(Interview, interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        if random.random() < 0.10:
            error_messages = [
                "AI feedback generation failed. Please try again.",
                "AI service is currently unavailable.",
                "AI model did not respond. Please retry.",
                "AI feedback system is temporarily unavailable."
            ]
            time.sleep(random.uniform(2, 4))
            raise ServiceUnavailableError(random.choice(error_messages))

        scores = interview.scores
        if not scores:
            avg_score = 0
        else:
            total = sum(s.score for s in scores)
            max_total = sum(s.max_score for s in scores)
            avg_score = (total / max_total) * 10 if max_total else 0

        if avg_score >= 8:
            bucket = HIGH_PERFORMANCE
        elif avg_score >= 5:
            bucket = MODERATE_PERFORMANCE
        else:
            bucket = LOW_PERFORMANCE

        summary = random.choice(bucket["summaries"])
        num_strengths = random.randint(3, 5)
        num_weaknesses = random.randint(3, 5)

        strengths = random.sample(bucket["strengths"], num_strengths)
        weaknesses = random.sample(bucket["weaknesses"], num_weaknesses)

        time.sleep(random.uniform(5, 13))

        return {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses
        }

    @staticmethod
    def generate_mock_feedback(db: Session, session_id: str) -> dict:
        """
        Generate AI feedback for a mock interview session.
        """
        session = db.get(MockInterview, session_id)
        if not session:
            raise NotFoundError("Mock interview session not found.")

        if not session.answer_text:
            raise ValidationError("Cannot generate feedback — no answer submitted yet.")

        if random.random() < 0.10:
            error_messages = [
                "AI feedback generation failed. Please try again.",
                "AI service is currently unavailable.",
                "AI model did not respond. Please retry.",
                "AI feedback system is temporarily unavailable.",
            ]
            time.sleep(random.uniform(2, 4))
            raise ServiceUnavailableError(random.choice(error_messages))

        answer = session.answer_text.strip()
        answer_lower = answer.lower()
        word_count = len(answer.split())

        score = 5

        if word_count >= 200:
            score += 2
        elif word_count >= 100:
            score += 1
        elif word_count < 30:
            score -= 2

        structure_signals = [
            "first", "second", "third", "finally",
            "for example", "such as", "because",
            "trade-off", "tradeoff", "consideration",
            "advantage", "disadvantage", "however",
            "approach", "solution", "strategy",
        ]
        signal_count = sum(1 for s in structure_signals if s in answer_lower)
        if signal_count >= 4:
            score += 2
        elif signal_count >= 2:
            score += 1

        category_keywords = {
            "behavioral": ["team", "challenge", "result", "learned", "outcome", "situation", "action"],
            "technical": ["complexity", "algorithm", "data structure", "time", "space", "implementation"],
            "system_design": ["scalability", "database", "cache", "load balancer", "api", "architecture"],
        }
        cat_words = category_keywords.get(session.category, [])
        cat_matches = sum(1 for kw in cat_words if kw in answer_lower)
        if cat_matches >= 3:
            score += 1

        score = max(1, min(10, score))

        if score >= 8:
            bucket = MOCK_HIGH
        elif score >= 5:
            bucket = MOCK_MODERATE
        else:
            bucket = MOCK_LOW

        summary = random.choice(bucket["summaries"])
        num_strengths = random.randint(2, 4)
        num_weaknesses = random.randint(2, 4)

        strengths = random.sample(
            bucket["strengths"], min(num_strengths, len(bucket["strengths"]))
        )
        weaknesses = random.sample(
            bucket["weaknesses"], min(num_weaknesses, len(bucket["weaknesses"]))
        )

        time.sleep(random.uniform(3, 8))

        session.ai_summary = summary
        session.ai_strengths = json.dumps(strengths)
        session.ai_weaknesses = json.dumps(weaknesses)
        session.ai_score = score
        session.ai_generated_at = datetime.now(timezone.utc)
        session.status = MockInterviewStatus.completed
        session.completed_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "score": score,
        }