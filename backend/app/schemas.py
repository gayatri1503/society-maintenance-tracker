from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from .models import UserRole, ComplaintStatus, Priority


# ---------- Auth ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    flat_number: Optional[str] = None
    role: UserRole = UserRole.resident


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    flat_number: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Complaint status history ----------

class StatusHistoryOut(BaseModel):
    id: int
    status: ComplaintStatus
    note: Optional[str] = None
    changed_by: int
    changed_at: datetime

    class Config:
        from_attributes = True


# ---------- Complaints ----------

class ComplaintCreate(BaseModel):
    category: str
    description: str


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus
    note: Optional[str] = None


class ComplaintPriorityUpdate(BaseModel):
    priority: Priority


class ComplaintOut(BaseModel):
    id: int
    resident_id: int
    category: str
    description: str
    photo_url: Optional[str] = None
    current_status: ComplaintStatus
    priority: Priority
    created_at: datetime
    history: List[StatusHistoryOut] = []
    is_overdue: bool = False

    class Config:
        from_attributes = True


# ---------- Notices ----------

class NoticeCreate(BaseModel):
    title: str
    body: str
    is_important: bool = False


class NoticeOut(BaseModel):
    id: int
    title: str
    body: str
    is_important: bool
    posted_by: int
    created_at: datetime

    class Config:
        from_attributes = True