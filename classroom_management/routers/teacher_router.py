from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from classroom_management.database import get_db
from classroom_management.models import User, Course, Schedule, Enrollment, Attendance, Grade
from classroom_management.schemas import (
    UserResponse, ScheduleResponse, AttendanceBatchSubmit,
    AttendanceResponse, GradeUpdate, GradeResponse, CourseResponse
)
from classroom_management.auth import require_roles

router = APIRouter(prefix="/api/teacher", tags=["Teacher"])

teacher_or_admin = require_roles(["teacher", "admin"])

@router.get("/students", response_model=List[UserResponse])
def get_students_list(
    course_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Xem danh sách hồ sơ học sinh."""
    query = db.query(User).filter(User.role == "student")
    
    if course_id:
        student_ids = db.query(Enrollment.student_id).filter(Enrollment.course_id == course_id).all()
        ids = [s[0] for s in student_ids]
        query = query.filter(User.id.in_(ids))
        
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_pattern)) | 
            (User.code.ilike(search_pattern)) |
            (User.username.ilike(search_pattern))
        )
        
    return query.all()

@router.get("/schedules", response_model=List[ScheduleResponse])
def get_teacher_schedules(
    week_number: Optional[int] = None,
    month_number: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Xem lịch dạy trong từng tuần, từng tháng của giáo viên."""
    query = db.query(Schedule)
    
    if current_user.role == "teacher":
        query = query.filter(Schedule.teacher_id == current_user.id)
        
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

@router.get("/schedules/{schedule_id}/students", response_model=List[UserResponse])
def get_students_for_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Lấy danh sách sinh viên học môn tương ứng với lịch dạy để điểm danh."""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch học!")
    
    if current_user.role == "teacher" and schedule.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không phải là giảng viên dạy buổi học này!")
    
    student_ids = db.query(Enrollment.student_id).filter(Enrollment.course_id == schedule.course_id).all()
    s_ids = [s[0] for s in student_ids]
    
    students = db.query(User).filter(User.id.in_(s_ids)).all()
    return students

@router.post("/attendance")
def submit_attendance(
    payload: AttendanceBatchSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Điểm danh học sinh cho một buổi học."""
    schedule = db.query(Schedule).filter(Schedule.id == payload.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch dạy!")
    
    if current_user.role == "teacher" and schedule.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không dạy buổi học này!")
    
    count = 0
    for record in payload.records:
        existing = db.query(Attendance).filter(
            Attendance.schedule_id == payload.schedule_id,
            Attendance.student_id == record.student_id,
            Attendance.attendance_date == payload.attendance_date
        ).first()
        
        if existing:
            existing.status = record.status
            existing.note = record.note
        else:
            new_att = Attendance(
                schedule_id=payload.schedule_id,
                student_id=record.student_id,
                attendance_date=payload.attendance_date,
                status=record.status,
                note=record.note
            )
            db.add(new_att)
        count += 1
        
    db.commit()
    return {"message": f"Đã cập nhật điểm danh thành công cho {count} học sinh!", "date": str(payload.attendance_date)}

@router.get("/attendance/{schedule_id}", response_model=List[AttendanceResponse])
def get_schedule_attendance(
    schedule_id: int,
    attendance_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Xem lại danh sách điểm danh theo lịch dạy và ngày."""
    records = db.query(Attendance).filter(
        Attendance.schedule_id == schedule_id,
        Attendance.attendance_date == attendance_date
    ).all()
    
    results = []
    for r in records:
        st = db.query(User).filter(User.id == r.student_id).first()
        res = AttendanceResponse.from_orm(r)
        res.student_name = st.full_name if st else ""
        res.student_code = st.code if st else ""
        results.append(res)
    return results

@router.get("/courses", response_model=List[CourseResponse])
def get_teacher_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Danh sách môn học dành cho giáo viên chọn cho điểm."""
    return db.query(Course).all()

@router.get("/courses/{course_id}/grades", response_model=List[GradeResponse])
def get_course_grades(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Xem danh sách điểm số học sinh của môn học do mình giảng dạy."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học!")
        
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    results = []
    
    if enrollments:
        students = [db.query(User).filter(User.id == en.student_id).first() for en in enrollments]
    else:
        # If no students enrolled via registration yet, allow grading any student in system
        students = db.query(User).filter(User.role == "student").all()

    for student in students:
        if not student:
            continue
        grade = db.query(Grade).filter(Grade.student_id == student.id, Grade.course_id == course_id).first()
        
        results.append(GradeResponse(
            id=grade.id if grade else 0,
            student_id=student.id,
            student_name=student.full_name,
            student_code=student.code,
            course_id=course_id,
            course_name=course.course_name,
            course_code=course.course_code,
            credits=course.credits,
            midterm_score=grade.midterm_score if grade else None,
            final_score=grade.final_score if grade else None,
            total_score=grade.total_score if grade else None,
            note=grade.note if grade else ""
        ))
    return results

@router.post("/grades", response_model=GradeResponse)
def submit_student_grade(
    payload: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin)
):
    """Nhập điểm cho từng sinh viên môn học mình dạy."""
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học!")
        
    student = db.query(User).filter(User.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên!")
        
    grade = db.query(Grade).filter(
        Grade.student_id == payload.student_id,
        Grade.course_id == payload.course_id
    ).first()

    mid = payload.midterm_score if payload.midterm_score is not None else (grade.midterm_score if grade else None)
    fin = payload.final_score if payload.final_score is not None else (grade.final_score if grade else None)
    
    tot = None
    if mid is not None and fin is not None:
        tot = round(mid * 0.4 + fin * 0.6, 2)
    elif fin is not None:
        tot = fin
    elif mid is not None:
        tot = mid

    if grade:
        grade.midterm_score = mid
        grade.final_score = fin
        grade.total_score = tot
        if payload.note is not None:
            grade.note = payload.note
        grade.graded_by_teacher_id = current_user.id
    else:
        grade = Grade(
            student_id=payload.student_id,
            course_id=payload.course_id,
            midterm_score=mid,
            final_score=fin,
            total_score=tot,
            note=payload.note,
            graded_by_teacher_id=current_user.id
        )
        db.add(grade)

    db.commit()
    db.refresh(grade)

    return GradeResponse(
        id=grade.id,
        student_id=student.id,
        student_name=student.full_name,
        student_code=student.code,
        course_id=course.id,
        course_name=course.course_name,
        course_code=course.course_code,
        credits=course.credits,
        midterm_score=grade.midterm_score,
        final_score=grade.final_score,
        total_score=grade.total_score,
        note=grade.note
    )
