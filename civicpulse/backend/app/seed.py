import os
from sqlalchemy.orm import Session
from app.models.models import Category, Department, User, UserRole
from app.core.security import hash_password

DEFAULT_CATEGORIES = [
    (1, "Roads & Potholes", 75.0),
    (2, "Garbage & Sanitation", 70.0),
    (3, "Drainage & Waterlogging", 85.0),
    (4, "Streetlights & Electricity", 65.0),
    (5, "Water Supply", 80.0),
    (6, "Public Infrastructure", 45.0),
    (7, "Other Civic Issues", 40.0),
]

DEFAULT_DEPARTMENTS = [
    "PWD Roads",
    "Sanitation",
    "Drainage",
    "Electrical",
    "Water Works",
    "Parks & Public Works",
]


def seed_database(db: Session):
    for cat_id, name, severity in DEFAULT_CATEGORIES:
        if not db.query(Category).filter(Category.category_id == cat_id).first():
            db.add(Category(category_id=cat_id, category_name=name, base_severity=severity))

    for dept_name in DEFAULT_DEPARTMENTS:
        if not db.query(Department).filter(Department.name == dept_name).first():
            db.add(Department(name=dept_name))

    superadmin_name = os.getenv("SUPERADMIN_NAME", "Municipal SuperAdmin").strip()
    superadmin_email = os.getenv("SUPERADMIN_EMAIL", "").strip().lower()
    superadmin_password = os.getenv("SUPERADMIN_PASSWORD", "")

    if superadmin_email and superadmin_password:
        if not db.query(User).filter(User.email == superadmin_email).first():
            db.add(
                User(
                    name=superadmin_name,
                    email=superadmin_email,
                    password_hash=hash_password(superadmin_password),
                    role=UserRole.superadmin,
                )
            )

    db.commit()
