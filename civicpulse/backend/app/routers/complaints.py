from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Complaint,
    ComplaintStatus,
    StatusHistory,
    User,
    Vote,
)
from app.schemas.schemas import ComplaintOut, StatusUpdateRequest
from app.core.security import ADMIN_ROLES, get_current_user, bearer_scheme
from app.services.storage import save_uploaded_image
from app.services.duplicate import flag_duplicate_candidates
from app.services.priority import calculate_priority_score

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])


def serialize_complaint(c: Complaint) -> ComplaintOut:
    return ComplaintOut(
        complaint_id=c.complaint_id,
        category_id=c.category_id,
        description=c.description,
        latitude=c.latitude,
        longitude=c.longitude,
        image_url=c.image_url,
        resolution_image_url=c.resolution_image_url,
        rejection_reason=c.rejection_reason,
        status=c.status,
        priority_score=c.priority_score,
        votes=len(c.votes),
        department=c.department.name if c.department else None,
        merged_into_id=c.merged_into_id,
        created_at=c.created_at,
        updated_at=c.updated_at,
        history=sorted(c.status_history, key=lambda h: h.timestamp),
    )


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    category_id: int = Form(...),
    description: str = Form(..., min_length=5),
    latitude: float = Form(...),
    longitude: float = Form(...),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url = None
    if photo and photo.filename:
        image_url = await save_uploaded_image(photo)

    complaint = Complaint(
        user_id=current_user.user_id,
        category_id=category_id,
        description=description.strip(),
        latitude=latitude,
        longitude=longitude,
        image_url=image_url,
        status=ComplaintStatus.submitted,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Record initial audit trail
    db.add(
        StatusHistory(
            complaint_id=complaint.complaint_id,
            status=ComplaintStatus.submitted,
            note="Citizen submitted civic complaint.",
            updated_by=current_user.user_id,
        )
    )

    # Run dual-signal duplicate candidate check & weighted priority scoring
    flag_duplicate_candidates(db, complaint)
    complaint.priority_score = calculate_priority_score(db, complaint)
    db.commit()
    db.refresh(complaint)

    return serialize_complaint(complaint)


@router.get("", response_model=List[ComplaintOut])
def list_complaints(
    category_id: Optional[int] = Query(None),
    status_filter: Optional[ComplaintStatus] = Query(None, alias="status"),
    mine: bool = Query(False),
    db: Session = Depends(get_db),
    credentials=Depends(bearer_scheme),
):
    query = db.query(Complaint).filter(Complaint.merged_into_id.is_(None))

    if category_id:
        query = query.filter(Complaint.category_id == category_id)
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if mine:
        user = get_current_user(credentials=credentials, db=db)
        query = query.filter(Complaint.user_id == user.user_id)

    complaints = query.order_by(Complaint.priority_score.desc(), Complaint.created_at.desc()).all()
    return [serialize_complaint(c) for c in complaints]


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    return serialize_complaint(complaint)


@router.post("/{complaint_id}/vote")
def vote_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    vote = Vote(complaint_id=complaint_id, user_id=current_user.user_id)
    db.add(vote)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="You have already voted for this issue.")

    complaint.priority_score = calculate_priority_score(db, complaint)
    db.commit()
    vote_count = db.query(Vote).filter(Vote.complaint_id == complaint_id).count()
    return {"complaint_id": complaint_id, "votes": vote_count, "priority_score": complaint.priority_score}


@router.patch("/{complaint_id}/status", response_model=ComplaintOut)
def update_complaint_status(
    complaint_id: int,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    is_admin = current_user.role in ADMIN_ROLES

    # Citizens may only reopen their own resolved complaints
    if not is_admin:
        if complaint.user_id != current_user.user_id or payload.status != ComplaintStatus.reopened:
            raise HTTPException(status_code=403, detail="Only municipal officials can update this status.")
        if complaint.status != ComplaintStatus.resolved:
            raise HTTPException(status_code=400, detail="Only resolved complaints can be reopened.")

    if payload.status == ComplaintStatus.rejected and not payload.rejection_reason:
        raise HTTPException(status_code=400, detail="A rejection reason is required.")

    complaint.status = payload.status
    if payload.department_id is not None and is_admin:
        complaint.department_id = payload.department_id
    if payload.rejection_reason:
        complaint.rejection_reason = payload.rejection_reason

    db.add(
        StatusHistory(
            complaint_id=complaint.complaint_id,
            status=payload.status,
            note=payload.note or payload.rejection_reason or f"Status updated to {payload.status.value}.",
            updated_by=current_user.user_id,
        )
    )
    complaint.priority_score = calculate_priority_score(db, complaint)
    db.commit()
    db.refresh(complaint)
    return serialize_complaint(complaint)