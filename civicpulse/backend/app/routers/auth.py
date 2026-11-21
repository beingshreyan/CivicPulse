from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import AdminInvite, User, UserRole
from app.schemas.schemas import UserRegister, UserLogin, UserPublic, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email is already registered.")

    user = User(
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        role=UserRole.citizen,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/admin-register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def admin_register(payload: UserRegister, db: Session = Depends(get_db)):
    email = payload.email.lower()
    invite = (
        db.query(AdminInvite)
        .filter(AdminInvite.email == email, AdminInvite.is_used == 0)
        .first()
    )
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This email is not authorized for admin registration. Contact your Manager.",
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email is already registered.")

    user = User(
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        role=invite.role,
        department_id=invite.department_id,
    )
    invite.is_used = 1
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    email = payload.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.user_id, user.role)
    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user