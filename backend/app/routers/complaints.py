import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, require_admin
from ..cloudinary_utils import upload_complaint_photo

router = APIRouter(prefix="/complaints", tags=["complaints"])

OVERDUE_THRESHOLD_DAYS = int(os.getenv("OVERDUE_THRESHOLD_DAYS", 7))


def _attach_overdue_flag(complaint: models.Complaint) -> schemas.ComplaintOut:
    out = schemas.ComplaintOut.model_validate(complaint)
    out.is_overdue = complaint.check_overdue(OVERDUE_THRESHOLD_DAYS)
    return out


@router.post("", response_model=schemas.ComplaintOut, status_code=201)
async def create_complaint(
    category: str = Form(...),
    description: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    photo_url = None
    if photo is not None:
        file_bytes = await photo.read()
        unique_id = f"{current_user.id}_{uuid.uuid4().hex}"
        photo_url = upload_complaint_photo(file_bytes, unique_id)

    complaint = models.Complaint(
        resident_id=current_user.id,
        category=category,
        description=description,
        photo_url=photo_url,
        current_status=models.ComplaintStatus.open,
        priority=models.Priority.low,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # First history row — the complaint's "birth" event
    first_history = models.ComplaintStatusHistory(
        complaint_id=complaint.id,
        status=models.ComplaintStatus.open,
        note="Complaint raised",
        changed_by=current_user.id,
    )
    db.add(first_history)
    db.commit()
    db.refresh(complaint)

    return _attach_overdue_flag(complaint)