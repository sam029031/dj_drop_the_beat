"""課程模型。"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class DifficultyEnum(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    instructor = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    duration_hours = Column(Float, nullable=False)
    max_students = Column(Integer, default=30)
    current_students = Column(Integer, default=0)
    syllabus = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)
    learning_outcomes = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False)
    class_schedule = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    registration_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def name(self):
        return self.title

    @property
    def hours(self):
        return self.duration_hours

    @property
    def lessons(self):
        return max(1, int(round((self.duration_hours or 0) / 2)))

    @property
    def location(self):
        return "DJ 教室 / 線下課程"

    @property
    def requirements(self):
        return self.prerequisites

class CourseRegistration(Base):
    __tablename__ = "course_registrations"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="Active")
    paid = Column(Boolean, default=False)
    registered_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
