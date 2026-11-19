import math
import re
from typing import List
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import Complaint, ComplaintStatus, DuplicateReview, DuplicateDecision

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "in", "on", "at", "to",
    "for", "of", "and", "or", "near", "beside", "outside", "this", "that",
    "with", "from", "by", "very", "there", "here",
}


def normalize_tokens(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}


def jaccard_similarity(text_a: str, text_b: str) -> float:
    tokens_a = normalize_tokens(text_a)
    tokens_b = normalize_tokens(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return round(len(intersection) / len(union), 4)


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return round(r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def flag_duplicate_candidates(db: Session, new_complaint: Complaint) -> List[DuplicateReview]:
    active_statuses = [
        ComplaintStatus.submitted,
        ComplaintStatus.under_review,
        ComplaintStatus.accepted,
        ComplaintStatus.in_progress,
        ComplaintStatus.reopened,
    ]

    existing = (
        db.query(Complaint)
        .filter(
            Complaint.complaint_id != new_complaint.complaint_id,
            Complaint.category_id == new_complaint.category_id,
            Complaint.status.in_(active_statuses),
            Complaint.merged_into_id.is_(None),
        )
        .all()
    )

    flagged: List[DuplicateReview] = []
    for candidate in existing:
        dist = haversine_meters(
            new_complaint.latitude,
            new_complaint.longitude,
            candidate.latitude,
            candidate.longitude,
        )
        if dist > settings.DUPLICATE_RADIUS_METERS:
            continue

        sim = jaccard_similarity(new_complaint.description, candidate.description)
        if sim >= settings.DUPLICATE_TEXT_SIMILARITY:
            review = DuplicateReview(
                complaint_id=new_complaint.complaint_id,
                candidate_id=candidate.complaint_id,
                similarity_score=sim,
                geographic_distance=dist,
                decision=DuplicateDecision.pending,
            )
            db.add(review)
            flagged.append(review)

    if flagged:
        db.commit()
    return flagged