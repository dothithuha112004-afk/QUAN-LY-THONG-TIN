from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from classroom_management.database import get_db
from classroom_management.models import User
from classroom_management.schemas import UserLogin, Token, UserResponse, UserProfileUpdate, ChangePasswordRequest
from classroom_management.auth import verify_password, hash_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    """User Login endpoint."""
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác!"
        )
    
    token_data = {"sub": user.username, "role": user.role, "user_id": user.id}
    access_token = create_access_token(token_data)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=86400
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name
    }

@router.post("/logout")
def logout(response: Response):
    """User Logout endpoint."""
    response.delete_cookie(key="access_token")
    return {"message": "Đã đăng xuất thành công"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user profile."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update profile fields (Họ tên, Tuổi, Chức vị, Bộ môn, Email, SĐT)."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.email is not None:
        current_user.email = payload.email
    if payload.phone is not None:
        current_user.phone = payload.phone
    if payload.age is not None:
        current_user.age = payload.age
    if payload.title is not None:
        current_user.title = payload.title
    if payload.department is not None:
        current_user.department = payload.department
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url

    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Đổi mật khẩu tài khoản người dùng."""
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác!"
        )
    if len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải có ít nhất 6 ký tự!"
        )
    
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công! Vui lòng sử dụng mật khẩu mới cho lần đăng nhập sau."}
