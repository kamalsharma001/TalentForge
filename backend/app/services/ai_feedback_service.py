"""
AiFeedbackService — generates interview evaluation summaries
using a rule-based system driven by interview scores.

Features:
1. Calculates candidate average score
2. Selects performance bucket (High / Moderate / Low)
3. Randomly selects summaries, strengths, weaknesses
4. Simulates AI processing delay (5–10 seconds)
5. Simulates AI service failure with 10% probability
"""

import logging
import random
import time

from app.models.interview import Interview
from app.utils.errors import NotFoundError, ServiceUnavailableError

from app.templates.ai_feedback_templates import (
    HIGH_PERFORMANCE,
    MODERATE_PERFORMANCE,
    LOW_PERFORMANCE
)

logger = logging.getLogger(__name__)


class AiFeedbackService:

    @staticmethod
    def generate(interview_id: str) -> dict:

        interview = Interview.query.get(interview_id)

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