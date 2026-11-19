from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Complaint,
    ComplaintStatus,
    Department,
    DuplicateDecision,
    DuplicateReview,
    StatusHistory,
    User,
    UserRole,
)
from app.schemas.schemas import DuplicateDecisionRequest, DuplicateReviewOut, UserPublic
from app.core.security import require_admin, require_roles
from app.services.storage import save_uploaded_image
from app.services.priority import calculate_priority_score

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])


@router.get("/departments")
def list_departments(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    depts = db.query(Department).order_by(Department.name).all()
    return [{"department_id": d.department_id, "name": d.name} for d in depts]


@router.get("/duplicates", response_model=List[DuplicateReviewOut])
def list_pending_duplicates(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return (
        db.query(DuplicateReview)
        .filter(DuplicateReview.decision == DuplicateDecision.pending)
        .order_by(DuplicateReview.similarity_score.desc())
        .all()
    )


@router.post("/duplicates/{review_id}/decide", response_model=DuplicateReviewOut)
def decide_duplicate(
    review_id: int,
    payload: DuplicateDecisionRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    review = db.query(DuplicateReview).filter(DuplicateReview.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Duplicate review record not found.")

    if payload.decision == DuplicateDecision.pending:
        raise HTTPException(status_code=400, detail="Decision must be 'merged' or 'separate'.")

    review.decision = payload.decision
    review.reviewed_by = admin.user_id

    if payload.decision == DuplicateDecision.merged:
        dup_complaint = db.query(Complaint).filter(Complaint.complaint_id == review.complaint_id).first()
        primary = db.query(Complaint).filter(Complaint.complaint_id == review.candidate_id).first()
        if dup_complaint and primary:
            dup_complaint.merged_into_id = primary.complaint_id
            db.add(
                StatusHistory(
                    complaint_id=primary.complaint_id,
                    status=primary.status,
                    note=f"Merged duplicate report CP-{dup_complaint.complaint_id} into this ticket.",
                    updated_by=admin.user_id,
                )
            )
            primary.priority_score = calculate_priority_score(db, primary)

    db.commit()
    db.refresh(review)
    return review


@router.post("/complaints/{complaint_id}/resolution-photo")
async def upload_resolution_photo(
    complaint_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    image_url = await save_uploaded_image(photo)
    complaint.resolution_image_url = image_url
    complaint.status = ComplaintStatus.resolved

    db.add(
        StatusHistory(
            complaint_id=complaint.complaint_id,
            status=ComplaintStatus.resolved,
            note="Official resolution photographic evidence uploaded.",
            updated_by=admin.user_id,
        )
    )
    db.commit()
    return {"complaint_id": complaint_id, "resolution_image_url": image_url, "status": "resolved"}


@router.get("/users", response_model=List[UserPublic])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles([UserRole.superadmin])),
):
    return db.query(User).order_by(User.user_id).all()


@router.patch("/users/{user_id}/role", response_model=UserPublic)
def update_user_role(
    user_id: int,
    role: UserRole,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles([UserRole.superadmin])),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.role = role
    db.commit()
    db.refresh(user)
    return user