import enum
from datetime import datetime, timedelta
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from .database import Base


class UserRole(str, enum.Enum):
    resident = "resident"
    admin = "admin"


class ComplaintStatus(str, enum.Enum):
    open = "Open"
    in_progress = "In Progress"
    resolved = "Resolved"


class Priority(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.resident)
    flat_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="resident")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    photo_url = Column(String, nullable=True)
    current_status = Column(SQLEnum(ComplaintStatus), nullable=False, default=ComplaintStatus.open)
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.low)
    created_at = Column(DateTime, default=datetime.utcnow)

    resident = relationship("User", back_populates="complaints")
    history = relationship("ComplaintStatusHistory", back_populates="complaint", order_by="ComplaintStatusHistory.changed_at")

    def is_overdue(self, threshold_days: int) -> bool:
        if self.current_status == ComplaintStatus.resolved:
            return False
        age = datetime.utcnow() - self.created_at
        return age > timedelta(days=threshold_days)


class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    status = Column(SQLEnum(ComplaintStatus), nullable=False)
    note = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="history")


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    is_important = Column(Boolean, default=False)
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)