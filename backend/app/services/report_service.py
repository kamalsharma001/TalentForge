"""
ReportService — manages the InterviewReport lifecycle.
"""

from datetime import datetime, timezone

from app import db
from app.models.interview import Interview, InterviewStatus
from app.models.interview_report import InterviewReport, ReportDecision
from app.models.interviewer import Interviewer
from app.schemas.report_schema import InterviewReportSchema, CandidateReportSchema
from app.utils.errors import NotFoundError, ConflictError, ForbiddenError

_schema           = InterviewReportSchema()
_candidate_schema = CandidateReportSchema()


class ReportService:

    # ── Create ────────────────────────────────────────────────────────────
    @staticmethod
    def create(interview_id: str, data: dict, interviewer_user_id: str) -> dict:
        interview = Interview.query.get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status != InterviewStatus.report_pending:
            raise ConflictError("A report can only be created for completed interviews.")

        interviewer = Interviewer.query.filter_by(user_id=interviewer_user_id).first()
        if not interviewer or str(interview.interviewer_id) != str(interviewer.id):
            raise ForbiddenError("Only the assigned interviewer can submit this report.")

        if interview.report:
            raise ConflictError("A report already exists for this interview.")

        decision_raw = data.get("decision")
        decision = ReportDecision(decision_raw) if decision_raw else None

        report = InterviewReport(
            interview_id=interview.id,
            summary=data.get("summary"),
            strengths=data.get("strengths"),
            weaknesses=data.get("weaknesses"),
            recommendation=data.get("recommendation"),
            private_notes=data.get("private_notes"),
            decision=decision,
        )
        ReportService._compute_overall_score(report, interview)

        db.session.add(report)

        interview.status = InterviewStatus.completed
        db.session.commit()
        return _schema.dump(report)

    # ── Update ────────────────────────────────────────────────────────────
    @staticmethod
    def update(report_id: str, data: dict, requesting_user_id: str) -> dict:
        report = InterviewReport.query.get(report_id)
        if not report:
            raise NotFoundError("Report not found.")

        if report.is_published:
            raise ConflictError("Published reports cannot be edited.")

        for field in ("summary", "strengths", "weaknesses", "recommendation", "private_notes"):
            if field in data:
                setattr(report, field, data[field])

        if "decision" in data and data["decision"]:
            report.decision = ReportDecision(data["decision"])

        ReportService._compute_overall_score(report, report.interview)

        if report.decision:
            report.is_published = True
            report.published_at = datetime.now(timezone.utc)

        db.session.commit()
        return _schema.dump(report)

    # ── Get by interview ──────────────────────────────────────────────────
    @staticmethod
    def get_by_interview(interview_id: str, as_candidate: bool = False) -> dict:
        report = InterviewReport.query.filter_by(interview_id=interview_id).first()
        if not report:
            raise NotFoundError("Report not found for this interview.")
        if as_candidate and not report.is_published:
            raise NotFoundError("Report is not yet available.")
        schema = _candidate_schema if as_candidate else _schema
        return schema.dump(report)

    # ── Publish ───────────────────────────────────────────────────────────
    @staticmethod
    def publish(report_id: str) -> dict:
        report = InterviewReport.query.get(report_id)
        if not report:
            raise NotFoundError("Report not found.")
        if report.is_published:
            raise ConflictError("Report is already published.")

        report.is_published = True
        report.published_at = datetime.now(timezone.utc)
        db.session.commit()
        return _schema.dump(report)

    # ── Attach AI summary ─────────────────────────────────────────────────
    @staticmethod
    def attach_ai_summary(report_id: str, ai_data: dict) -> None:
        report = InterviewReport.query.get(report_id)
        if not report:
            return
        report.ai_summary      = ai_data.get("summary")
        report.ai_strengths    = ai_data.get("strengths")
        report.ai_weaknesses   = ai_data.get("weaknesses")
        report.ai_generated_at = datetime.now(timezone.utc)
        db.session.commit()

    # ── Internal helpers ──────────────────────────────────────────────────
    @staticmethod
    def _compute_overall_score(report: InterviewReport, interview: Interview) -> None:
        """Average the interview scores and store on the report."""
        scores = interview.scores
        if not scores:
            return
        total = sum(s.score for s in scores)
        max_t = sum(s.max_score for s in scores)
        report.overall_score = round((total / max_t) * 10, 2) if max_t else None
