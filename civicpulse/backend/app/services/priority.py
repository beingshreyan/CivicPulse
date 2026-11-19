from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import Complaint, Category, Vote
from app.services.duplicate import haversine_meters


def calculate_priority_score(db: Session, complaint: Complaint) -> float:
    # 1. Severity (0-100) from category baseline
    category = db.query(Category).filter(Category.category_id == complaint.category_id).first()
    severity_score = category.base_severity if category else 50.0

    # 2. Community Support (0-100): votes + merged duplicates (caps at 50 votes = 100)
    vote_count = db.query(Vote).filter(Vote.complaint_id == complaint.complaint_id).count()
    merged_count = (
        db.query(Complaint)
        .filter(Complaint.merged_into_id == complaint.complaint_id)
        .count()
    )
    support_score = min(100.0, (vote_count + merged_count * 2) * 2.0)

    # 3. Waiting Time (0-100): elapsed days since creation (caps at 10 days = 100)
    now = datetime.now(timezone.utc)
    created = complaint.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    days_elapsed = max(0.0, (now - created).total_seconds() / 86400.0)
    waiting_score = min(100.0, days_elapsed * 10.0)

    # 4. Area Repetition (0-100): same-category complaints within 250m (caps at 5 = 100)
    nearby_same_cat = (
        db.query(Complaint)
        .filter(
            Complaint.category_id == complaint.category_id,
            Complaint.complaint_id != complaint.complaint_id,
        )
        .all()
    )
    repeat_count = sum(
        1
        for other in nearby_same_cat
        if haversine_meters(complaint.latitude, complaint.longitude, other.latitude, other.longitude) <= 250.0
    )
    repetition_score = min(100.0, repeat_count * 20.0)

    score = (
        settings.WEIGHT_SEVERITY * severity_score
        + settings.WEIGHT_SUPPORT * support_score
        + settings.WEIGHT_WAITING_TIME * waiting_score
        + settings.WEIGHT_REPETITION * repetition_score
    )
    return round(score, 2)