from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from .. import models
from ..deps import require_admin
from .complaints import OVERDUE_THRESHOLD_DAYS

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin),
):
    # Total by status
    status_counts = (
        db.query(models.Complaint.current_status, func.count(models.Complaint.id))
        .group_by(models.Complaint.current_status)
        .all()
    )
    by_status = {status.value: count for status, count in status_counts}

    # Total by category
    category_counts = (
        db.query(models.Complaint.category, func.count(models.Complaint.id))
        .group_by(models.Complaint.category)
        .all()
    )
    by_category = {category: count for category, count in category_counts}

    # Overdue count — computed in Python since it depends on created_at + threshold,
    # not a simple stored column
    all_open = (
        db.query(models.Complaint)
        .filter(models.Complaint.current_status != models.ComplaintStatus.resolved)
        .all()
    )
    overdue_count = sum(1 for c in all_open if c.check_overdue(OVERDUE_THRESHOLD_DAYS))

    total_complaints = sum(by_status.values())

    return {
        "total_complaints": total_complaints,
        "by_status": by_status,
        "by_category": by_category,
        "overdue_count": overdue_count,
    }