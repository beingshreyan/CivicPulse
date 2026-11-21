from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.models import UserRole, ComplaintStatus, DuplicateDecision


# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    user_id: int
    name: str
    email: str
    role: UserRole

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# --- Complaint Schemas ---
class StatusHistoryOut(BaseModel):
    status: ComplaintStatus
    note: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ComplaintOut(BaseModel):
    complaint_id: int
    category_id: int
    description: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    resolution_image_url: Optional[str] = None
    rejection_reason: Optional[str] = None
    status: ComplaintStatus
    priority_score: float
    votes: int = 0
    department: Optional[str] = None
    merged_into_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    history: List[StatusHistoryOut] = []

    class Config:
        from_attributes = True


class StatusUpdateRequest(BaseModel):
    status: ComplaintStatus
    department_id: Optional[int] = None
    note: Optional[str] = Field(None, max_length=500)
    rejection_reason: Optional[str] = Field(None, max_length=500)


# --- Duplicate Review Schemas ---
class DuplicateReviewOut(BaseModel):
    review_id: int
    complaint_id: int
    candidate_id: int
    similarity_score: float
    geographic_distance: float
    decision: DuplicateDecision
    created_at: datetime

    class Config:
        from_attributes = True


class DuplicateDecisionRequest(BaseModel):
    decision: DuplicateDecision  # merged | separate


# --- Analytics Schemas ---
class AnalyticsOut(BaseModel):
    active_reports: int
    total_reports: int
    total_votes: int
    verified_percentage: float
    resolved_count: int
    by_category: dict
    by_status: dict