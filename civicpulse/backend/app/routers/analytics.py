from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Category, Complaint, ComplaintStatus, Vote
from app.schemas.schemas import AnalyticsOut

router = APIRouter(prefix="/api/analytics", tags=["Public Analytics"])


@router.get("", response_model=AnalyticsOut)
def get_analytics(db: Session = Depends(get_db)):
    base_q = db.query(Complaint).filter(Complaint.merged_into_id.is_(None))
    total_reports = base_q.count()
    resolved_count = base_q.filter(Complaint.status == ComplaintStatus.resolved).count()
    rejected_count = base_q.filter(Complaint.status == ComplaintStatus.rejected).count()
    active_reports = total_reports - resolved_count - rejected_count

    verified_statuses = [
        ComplaintStatus.accepted,
        ComplaintStatus.in_progress,
        ComplaintStatus.resolved,
        ComplaintStatus.reopened,
    ]
    verified_count = base_q.filter(Complaint.status.in_(verified_statuses)).count()
    verified_pct = round((verified_count / total_reports) * 100, 1) if total_reports else 0.0

    total_votes = db.query(Vote).count()

    cat_rows = (
        db.query(Category.category_name, func.count(Complaint.complaint_id))
        .outerjoin(Complaint, Category.category_id == Complaint.category_id)
        .group_by(Category.category_name)
        .all()
    )
    by_category = {name: count for name, count in cat_rows}

    status_rows = (
        db.query(Complaint.status, func.count(Complaint.complaint_id))
        .filter(Complaint.merged_into_id.is_(None))
        .group_by(Complaint.status)
        .all()
    )
    by_status = {st.value: count for st, count in status_rows}

    return AnalyticsOut(
        active_reports=active_reports,
        total_reports=total_reports,
        total_votes=total_votes,
        verified_percentage=verified_pct,
        resolved_count=resolved_count,
        by_category=by_category,
        by_status=by_status,
    )