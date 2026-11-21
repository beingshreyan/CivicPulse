import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    citizen = "citizen"
    analyst = "analyst"
    updater = "updater"
    dispatcher = "dispatcher"
    reviewer = "reviewer"
    manager = "manager"
    superadmin = "superadmin"

class ComplaintStatus(str, enum.Enum):
    submitted = "submitted"
    under_review = "under_review"
    accepted = "accepted"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"
    reopened = "reopened"


class DuplicateDecision(str, enum.Enum):
    pending = "pending"
    merged = "merged"
    separate = "separate"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.citizen, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)

    complaints = relationship("Complaint", back_populates="reporter", foreign_keys="Complaint.user_id")
    votes = relationship("Vote", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False)
    base_severity = Column(Float, default=50.0, nullable=False)  # 0-100 baseline urgency

    complaints = relationship("Complaint", back_populates="category")


class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)

    complaints = relationship("Complaint", back_populates="department")


class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    merged_into_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=True)

    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    image_url = Column(Text, nullable=True)
    resolution_image_url = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.submitted, nullable=False, index=True)
    priority_score = Column(Float, default=0.0, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    reporter = relationship("User", back_populates="complaints", foreign_keys=[user_id])
    category = relationship("Category", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    votes = relationship("Vote", back_populates="complaint", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="complaint", cascade="all, delete-orphan")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("complaint_id", "user_id", name="uq_complaint_user_vote"),)

    vote_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    complaint = relationship("Complaint", back_populates="votes")
    user = relationship("User", back_populates="votes")


class StatusHistory(Base):
    __tablename__ = "status_history"

    status_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ComplaintStatus), nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    complaint = relationship("Complaint", back_populates="status_history")


class DuplicateReview(Base):
    __tablename__ = "duplicate_reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("complaints.complaint_id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    geographic_distance = Column(Float, nullable=False)
    decision = Column(Enum(DuplicateDecision), default=DuplicateDecision.pending, nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AdminInvite(Base):
    __tablename__ = "admin_invites"

    invite_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    is_used = Column(Integer, default=0, nullable=False)  # 0 = pending, 1 = registered
    invited_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))