"""課程業務邏輯"""
from sqlalchemy.orm import Session
from app.models.course import Course, CourseRegistration
from app.core.utils import get_current_datetime
import uuid

class CourseService:
    @staticmethod
    def get_active_courses(db: Session, page: int = 1, page_size: int = 20, sort: str = "created") -> tuple:
        skip = (page - 1) * page_size
        query = db.query(Course).filter(Course.is_active == True)
        total = query.count()
        if sort == "difficulty":
            query = query.order_by(Course.difficulty.asc(), Course.created_at.desc())
        else:
            query = query.order_by(Course.created_at.desc())
        return query.offset(skip).limit(page_size).all(), total

    @staticmethod
    def register_course(db: Session, user_id: int | None, course_id: int, name: str, email: str, phone: str, notes: str | None = None) -> CourseRegistration:
        course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
        if not course:
            raise ValueError("課程不存在")
        if course.max_students and course.current_students >= course.max_students:
            raise ValueError("課程已滿員")
        now = get_current_datetime()
        if course.registration_deadline and now > course.registration_deadline:
            raise ValueError("報名已截止")
        if user_id:
            existing = db.query(CourseRegistration).filter(
                CourseRegistration.course_id == course_id,
                CourseRegistration.user_id == user_id
            ).first()
            if existing:
                raise ValueError("已報名此課程")

        registration = CourseRegistration(
            course_id=course_id,
            user_id=user_id,
            registration_number=f"CRS-{uuid.uuid4().hex[:8].upper()}",
            name=name,
            email=email,
            phone=phone,
            notes=notes
        )
        course.current_students = (course.current_students or 0) + 1
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
