"""比賽模型。"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base

class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    venue = Column(String(200), nullable=False)
    entry_fee = Column(Float, default=0)
    prize_pool = Column(Float, nullable=True)
    rules = Column(Text, nullable=True)
    judging_criteria = Column(Text, nullable=True)
    registration_start = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=False, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    event_start_time = Column(String(10), nullable=True)
    max_participants = Column(Integer, default=100)
    current_participants = Column(Integer, default=0)
    min_age = Column(Integer, nullable=True)
    image_url = Column(String(255), nullable=True)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def name(self):
        return self.title

    @property
    def location(self):
        return self.venue

    @property
    def contest_date(self):
        return self.event_date

    @property
    def notes(self):
        return self.judging_criteria

class ContestRegistration(Base):
    __tablename__ = "contest_registrations"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    dj_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="Registered")
    paid = Column(Boolean, default=False)
    rank = Column(Integer, nullable=True)
    registered_at = Column(DateTime, server_default=func.now())
    participated_at = Column(DateTime, nullable=True)
