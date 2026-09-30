from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from classroom_management.database import get_db
from classroom_management.models import User, Course, Schedule, Enrollment, Grade, Attendance
from classroom_management.schemas import (
    CourseResponse, ScheduleResponse, GradeResponse, AttendanceResponse,
    CourseTuitionItem, TuitionSummaryResponse
)
from classroom_management.auth import require_roles

router = APIRouter(prefix="/api/student", tags=["Student"])

student_or_admin = require_roles(["student", "admin"])

@router.get("/tuition", response_model=TuitionSummaryResponse)
def get_student_tuition_summary(
    term: Optional[str] = "Học kỳ 1 - 2026",
    db: Session = Depends(get_db),
    current_user: User = Depends(student_or_admin)
):
    """Tra cứu chi tiết học phí từng môn học và tổng học phí trong học kỳ của sinh viên."""
    my_enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.term == term
    ).all()
    
    course_items = []
    total_credits = 0
    total_fee = 0.0
    
    for en in my_enrollments:
        course = db.query(Course).filter(Course.id == en.course_id).first()
        if course:
            fee_per_credit = course.tuition_fee or 1500000.0
            course_total = course.credits * fee_per_credit
            total_credits += course.credits
            total_fee += course_total
            
            course_items.append(CourseTuitionItem(
                course_id=course.id,
                course_code=course.course_code,
                course_name=course.course_name,
                credits=course.credits,
                fee_per_credit=fee_per_credit,
                total_course_fee=course_total,
                term=course.term
            ))
            
    return TuitionSummaryResponse(
        student_id=current_user.id,
        student_name=current_user.full_name,
        student_code=current_user.code,
        term=term,
        total_credits=total_credits,
        total_tuition_fee=total_fee,
        payment_status="Chờ thanh toán" if total_fee > 0 else "Hoàn thành",
        courses=course_items
    )

@router.get("/courses", response_model=List[CourseResponse])
def get_available_courses(
    term: Optional[str] = "Học kỳ 1 - 2026",
    db: Session = Depends(get_db),
    current_user: User = Depends(student_or_admin)
):
    """Danh sách các môn học có sẵn trong kỳ."""
    courses = db.query(Course).filter(Course.term == term).all()
    
    my_enrollments = db.query(Enrollment.course_id).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.term == term
    ).all()
    enrolled_course_ids = set([e[0] for e in my_enrollments])
    
    results = []
    for c in courses:
        res = CourseResponse.from_orm(c)
        res.is_enrolled = c.id in enrolled_course_ids
        results.append(res)
    return results

@router.post("/register/{course_id}")
def register_course(
    course_id: int,
    term: Optional[str] = "Học kỳ 1 - 2026",
    db: Session = Depends(get_db),
    current_user: User = Depends(student_or_admin)
):
    """Đăng ký môn học muốn học trong 1 kỳ."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học!")
        
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
        Enrollment.term == term
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Bạn đã đăng ký môn học này rồi!")
        
    enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course_id,
        term=term
    )
    db.add(enrollment)
    db.commit()
    return {"message": f"Đăng ký môn học '{course.course_name}' thành công!"}

@router.delete("/unregister/{course_id}")
def unregister_course(
    course_id: int,
    term: Optional[str] = "Học kỳ 1 - 2026",
    db: Session = Depends(get_db),
    current_user: User = Depends(student_or_admin)
):
    """Hủy đăng ký môn học."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
        Enrollment.term == term
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Bạn chưa đăng ký môn học này!")
        
    db.delete(enrollment)
    db.commit()
    return {"message": "Đã hủy đăng ký môn học thành công."}

@router.get("/schedules", response_model=List[ScheduleResponse])
def get_student_schedules(
    week_number: Optional[int] = None,
    month_number: Optional[int] = None,
    term: Optional[str] = "Học kỳ 1 - 2026",
    db: Session = Depends(get_db),
    current_user: User = Depends(student_or_admin)
):
    """Xem lịch học của sinh viên."""
    my_enrollments = db.query(Enrollment.course_id).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.term == term
    ).all()
    course_ids = [e[0] for e in my_enrollments]
    
    if not course_ids:
        return []
        
    query = db.query(Schedule).filter(Schedule.course_id.in_(course_ids))
    
    if week_number:
        query = query.filter(Schedule.week_number == week_number)
    if month_number:
        query = query.filter(Schedule.month_number == month_number)
        
    schedules = query.all()
    results = []
    for s in schedules:
        c = db.query(Course).filter(Course.id == s.course_id).first()
        t = db.query(User).filter(User.id == s.teacher_id).first()
        res = ScheduleResponse.from_orm(s)
        res.course_name = c.course_name if c else ""
        res.course_code = c.course_code if c else ""
        res.teacher_name = t.full_name if t else ""
        results.append(res)
    return results

@router.get("/grades", response_model=List[GradeResponse])
def get_student_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(student_or_admin)
):
    """Xem bảng điểm cá nhân các môn học đã đăng ký."""
    my_enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    results = []
    
    for en in my_enrollments:
        course = db.query(Course).filter(Course.id == en.course_id).first()
        grade = db.query(Grade).filter(
            Grade.student_id == current_user.id,
            Grade.course_id == en.course_id
        ).first()
        
        results.append(GradeResponse(
            id=grade.id if grade else 0,
            student_id=current_user.id,
            student_name=current_user.full_name,
            student_code=current_user.code,
            course_id=course.id,
            course_name=course.course_name,
            course_code=course.course_code,
            credits=course.credits,
            midterm_score=grade.midterm_score if grade else None,
            final_score=grade.final_score if grade else None,
            total_score=grade.total_score if grade else None,
            note=grade.note if grade else ""
        ))
    return results

@router.get("/attendance", response_model=List[AttendanceResponse])
def get_student_attendance_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(student_or_admin)
):
    """Xem lịch sử điểm danh cá nhân."""
    records = db.query(Attendance).filter(Attendance.student_id == current_user.id).all()
    results = []
    for r in records:
        res = AttendanceResponse.from_orm(r)
        res.student_name = current_user.full_name
        res.student_code = current_user.code
        results.append(res)
    return results
