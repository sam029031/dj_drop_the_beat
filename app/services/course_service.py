"""
課程業務邏輯
"""
from datetime import datetime
import logging
import uuid

from sqlalchemy.orm import Session

from app.models.course import Course, CourseRegistration

logger = logging.getLogger(__name__)


def _naive(dt):
    if dt is None:
        return None
    if getattr(dt, "tzinfo", None) is not None:
        return dt.replace(tzinfo=None)
    return dt


class CourseService:
    """課程業務邏輯"""

    @staticmethod
    def get_active_courses(db: Session, page: int = 1, page_size: int = 20) -> list:
        offset = (page - 1) * page_size
        return (
            db.query(Course)
            .filter(Course.is_active == True)
            .order_by(Course.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

    @staticmethod
    def register_course(
        db: Session,
        user_id: int | None,
        course_id: int,
        name: str,
        email: str,
        phone: str,
        notes: str | None = None,
    ) -> CourseRegistration:
        course = db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise ValueError("課程不存在")

        if course.current_students >= course.max_students:
            raise ValueError("課程已額滿")

        now = datetime.now()
        deadline = _naive(course.registration_deadline)
        if deadline is not None and now > deadline:
            raise ValueError("報名已截止")

        if user_id is not None:
            existing = (
                db.query(CourseRegistration)
                .filter(
                    CourseRegistration.course_id == course_id,
                    CourseRegistration.user_id == user_id,
                )
                .first()
            )
            if existing:
                raise ValueError("已報名此課程")

        registration_number = f"CRS-{uuid.uuid4().hex[:8].upper()}"

        registration = CourseRegistration(
            course_id=course_id,
            user_id=user_id,
            registration_number=registration_number,
            name=name,
            email=email,
            phone=phone,
            notes=notes,
        )

        course.current_students += 1

        db.add(registration)
        db.commit()
        db.refresh(registration)

        logger.info(f"課程報名: {registration_number}")
        return registration
