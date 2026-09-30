from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from classroom_management.database import get_db
from classroom_management.models import User, Course, Schedule, Enrollment, Grade, Attendance
from classroom_management.schemas import UserCreate, UserResponse, CourseCreate, CourseResponse, ScheduleCreate, ScheduleResponse
from classroom_management.auth import require_roles, hash_password

router = APIRouter(prefix="/api/admin", tags=["Admin"])

admin_only = require_roles(["admin"])

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """System Dashboard Summary Statistics."""
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_courses = db.query(Course).count()
    total_schedules = db.query(Schedule).count()
    return {
        "teachers_count": total_teachers,
        "students_count": total_students,
        "courses_count": total_courses,
        "schedules_count": total_schedules
    }

@router.get("/users", response_model=List[UserResponse])
def get_all_users(role: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Get all accounts with optional role filter."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.id.desc()).all()

@router.post("/users", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Create new account and assign role (admin/teacher/student)."""
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại!")
    
    new_user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role.lower(),
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        age=payload.age,
        title=payload.title,
        department=payload.department,
        code=payload.code
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(user_id: int, new_role: str, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Assign/change role for an existing account."""
    if new_role not in ["admin", "teacher", "student"]:
        raise HTTPException(status_code=400, detail="Quyền (role) không hợp lệ!")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản!")
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Delete a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản!")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản của chính mình!")
    
    db.delete(user)
    db.commit()
    return {"message": f"Đã xóa tài khoản {user.username} thành công."}

@router.get("/courses", response_model=List[CourseResponse])
def get_all_courses(db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Get list of all courses."""
    return db.query(Course).all()

@router.post("/courses", response_model=CourseResponse)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Create a new Course."""
    existing = db.query(Course).filter(Course.course_code == payload.course_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mã môn học đã tồn tại!")
    
    course = Course(
        course_code=payload.course_code,
        course_name=payload.course_name,
        credits=payload.credits,
        department=payload.department,
        description=payload.description,
        term=payload.term or "Học kỳ 1 - 2026"
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.post("/schedules", response_model=ScheduleResponse)
def create_schedule(payload: ScheduleCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Create a class schedule and assign a teacher."""
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học!")
    
    teacher = db.query(User).filter(User.id == payload.teacher_id, User.role.in_(["teacher", "admin"])).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Giáo viên không hợp lệ!")
    
    schedule = Schedule(
        course_id=payload.course_id,
        teacher_id=payload.teacher_id,
        room=payload.room,
        day_of_week=payload.day_of_week,
        start_time=payload.start_time,
        end_time=payload.end_time,
        week_number=payload.week_number,
        month_number=payload.month_number,
        term=payload.term or "Học kỳ 1 - 2026"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    res = ScheduleResponse.from_orm(schedule)
    res.course_name = course.course_name
    res.course_code = course.course_code
    res.teacher_name = teacher.full_name
    return res
