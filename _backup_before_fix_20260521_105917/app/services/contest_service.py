"""比賽業務邏輯"""
from sqlalchemy.orm import Session
from app.models.contest import Contest, ContestRegistration
from app.core.utils import get_current_datetime
import uuid

class ContestService:
    @staticmethod
    def get_active_contests(db: Session) -> list:
        now = get_current_datetime()
        return db.query(Contest).filter(
            Contest.is_active == True,
            Contest.event_date >= now
        ).order_by(Contest.event_date.asc()).all()

    @staticmethod
    def register_contest(db: Session, user_id: int | None, contest_id: int, name: str, email: str, phone: str, dj_name: str | None = None, notes: str | None = None) -> ContestRegistration:
        contest = db.query(Contest).filter(Contest.id == contest_id, Contest.is_active == True).first()
        if not contest:
            raise ValueError("比賽不存在")
        if contest.max_participants and contest.current_participants >= contest.max_participants:
            raise ValueError("比賽已滿員")
        now = get_current_datetime()
        if contest.registration_deadline and now > contest.registration_deadline:
            raise ValueError("報名已截止")
        if contest.event_date and now > contest.event_date:
            raise ValueError("比賽已結束")
        if user_id:
            existing = db.query(ContestRegistration).filter(
                ContestRegistration.contest_id == contest_id,
                ContestRegistration.user_id == user_id
            ).first()
            if existing:
                raise ValueError("已報名此比賽")

        registration = ContestRegistration(
            contest_id=contest_id,
            user_id=user_id,
            registration_number=f"CTT-{uuid.uuid4().hex[:8].upper()}",
            name=name,
            email=email,
            phone=phone,
            dj_name=dj_name,
            notes=notes
        )
        contest.current_participants = (contest.current_participants or 0) + 1
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
