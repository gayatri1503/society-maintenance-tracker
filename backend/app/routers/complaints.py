import os
import uuid
from datetime import datetime
from typing import Optional, List
from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
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

@router.get("/me", response_model=List[schemas.ComplaintOut])
def get_my_complaints(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    complaints = (
        db.query(models.Complaint)
        .options(joinedload(models.Complaint.history))
        .filter(models.Complaint.resident_id == current_user.id)
        .order_by(desc(models.Complaint.created_at))
        .all()
    )
    return [_attach_overdue_flag(c) for c in complaints]    


@router.get("", response_model=List[schemas.ComplaintOut])
def get_all_complaints(
    category: Optional[str] = Query(None),
    status_filter: Optional[models.ComplaintStatus] = Query(None, alias="status"),
    date_from: Optional[date_type] = Query(None),
    date_to: Optional[date_type] = Query(None),
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin),
):
    query = db.query(models.Complaint).options(joinedload(models.Complaint.history))

    if category:
        query = query.filter(models.Complaint.category == category)
    if status_filter:
        query = query.filter(models.Complaint.current_status == status_filter)
    if date_from:
        query = query.filter(models.Complaint.created_at >= date_from)
    if date_to:
        query = query.filter(models.Complaint.created_at <= date_to)

    complaints = query.order_by(desc(models.Complaint.created_at)).all()

    results = [_attach_overdue_flag(c) for c in complaints]

    # Surface overdue complaints at the top, most recent first within each group
    results.sort(key=lambda c: (not c.is_overdue, ))

    return results

@router.patch("/{complaint_id}/status", response_model=schemas.ComplaintOut)
def update_complaint_status(
    complaint_id: int,
    update: schemas.ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin),
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.current_status == models.ComplaintStatus.resolved:
        raise HTTPException(
            status_code=400,
            detail="Cannot update a resolved complaint — it is closed",
        )

    complaint.current_status = update.status

    history_entry = models.ComplaintStatusHistory(
        complaint_id=complaint.id,
        status=update.status,
        note=update.note,
        changed_by=admin_user.id,
    )
    db.add(history_entry)
    db.commit()
    db.refresh(complaint)

    # TODO (Step 7): trigger status-change email to resident here

    return _attach_overdue_flag(complaint)


@router.patch("/{complaint_id}/priority", response_model=schemas.ComplaintOut)
def update_complaint_priority(
    complaint_id: int,
    update: schemas.ComplaintPriorityUpdate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin),
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.priority = update.priority
    db.commit()
    db.refresh(complaint)

    return _attach_overdue_flag(complaint)
