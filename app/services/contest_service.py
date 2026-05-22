"""
比賽業務邏輯
"""
from datetime import datetime
import logging
import uuid

from sqlalchemy.orm import Session

from app.models.contest import Contest, ContestRegistration

logger = logging.getLogger(__name__)


def _naive(dt):
    if dt is None:
        return None
    if getattr(dt, "tzinfo", None) is not None:
        return dt.replace(tzinfo=None)
    return dt


class ContestService:
    """比賽業務邏輯"""

    @staticmethod
    def get_active_contests(db: Session) -> list:
        now = datetime.now()
        contests = (
            db.query(Contest)
            .filter(Contest.is_active == True)
            .order_by(Contest.event_date.asc())
            .all()
        )
        return [c for c in contests if _naive(c.event_date) and _naive(c.event_date) >= now]

    @staticmethod
    def register_contest(
        db: Session,
        user_id: int | None,
        contest_id: int,
        name: str,
        email: str,
        phone: str,
        dj_name: str | None = None,
        notes: str | None = None,
    ) -> ContestRegistration:
        contest = db.query(Contest).filter(Contest.id == contest_id).first()

        if not contest:
            raise ValueError("比賽不存在")

        if contest.current_participants >= contest.max_participants:
            raise ValueError("比賽已滿員")

        now = datetime.now()
        deadline = _naive(contest.registration_deadline)
        if deadline is None or now > deadline:
            raise ValueError("報名已截止")

        if user_id is not None:
            existing = (
                db.query(ContestRegistration)
                .filter(
                    ContestRegistration.contest_id == contest_id,
                    ContestRegistration.user_id == user_id,
                )
                .first()
            )
            if existing:
                raise ValueError("已報名此比賽")

        registration_number = f"CTT-{uuid.uuid4().hex[:8].upper()}"

        registration = ContestRegistration(
            contest_id=contest_id,
            user_id=user_id,
            registration_number=registration_number,
            name=name,
            email=email,
            phone=phone,
            dj_name=dj_name,
            notes=notes,
        )

        contest.current_participants += 1

        db.add(registration)
        db.commit()
        db.refresh(registration)

        logger.info(f"比賽報名: {registration_number}")
        return registration
