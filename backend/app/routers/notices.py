from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, require_admin

router = APIRouter(prefix="/notices", tags=["notices"])


@router.post("", response_model=schemas.NoticeOut, status_code=201)
def create_notice(
    notice_in: schemas.NoticeCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin),
):
    notice = models.Notice(
        title=notice_in.title,
        body=notice_in.body,
        is_important=notice_in.is_important,
        posted_by=admin_user.id,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)

    # TODO (Step 8): if is_important, trigger email to all residents here

    return notice


@router.get("", response_model=List[schemas.NoticeOut])
def get_notices(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    notices = (
        db.query(models.Notice)
        .order_by(desc(models.Notice.is_important), desc(models.Notice.created_at))
        .all()
    )
    return notices