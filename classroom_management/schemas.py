from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserLogin(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str # admin, teacher, student
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    title: Optional[str] = None
    department: Optional[str] = None
    code: Optional[str] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    title: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    title: Optional[str] = None
    department: Optional[str] = None
    code: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Course Schemas
class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    credits: int
    department: Optional[str] = None
    description: Optional[str] = None
    term: Optional[str] = "Học kỳ 1 - 2026"
    tuition_fee: Optional[float] = 1500000.0

class CourseResponse(BaseModel):
    id: int
    course_code: str
    course_name: str
    credits: int
    department: Optional[str] = None
    description: Optional[str] = None
    term: str
    tuition_fee: Optional[float] = 1500000.0
    is_enrolled: Optional[bool] = False

    class Config:
        from_attributes = True

# Tuition Schemas for Student
class CourseTuitionItem(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    credits: int
    fee_per_credit: float
    total_course_fee: float
    term: str

class TuitionSummaryResponse(BaseModel):
    student_id: int
    student_name: str
    student_code: Optional[str] = None
    term: str
    total_credits: int
    total_tuition_fee: float
    payment_status: str
    courses: List[CourseTuitionItem]

# Schedule Schemas
class ScheduleCreate(BaseModel):
    course_id: int
    teacher_id: int
    room: str
    day_of_week: str
    start_time: str
    end_time: str
    week_number: int
    month_number: int
    term: Optional[str] = "Học kỳ 1 - 2026"

class ScheduleResponse(BaseModel):
    id: int
    course_id: int
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    teacher_id: int
    teacher_name: Optional[str] = None
    room: str
    day_of_week: str
    start_time: str
    end_time: str
    week_number: int
    month_number: int
    term: str

    class Config:
        from_attributes = True

# Attendance Schemas
class AttendanceRecord(BaseModel):
    student_id: int
    status: str # Có mặt, Vắng mặt, Đi muộn, Có phép
    note: Optional[str] = None

class AttendanceBatchSubmit(BaseModel):
    schedule_id: int
    attendance_date: date
    records: List[AttendanceRecord]

class AttendanceResponse(BaseModel):
    id: int
    schedule_id: int
    student_id: int
    student_name: Optional[str] = None
    student_code: Optional[str] = None
    attendance_date: date
    status: str
    note: Optional[str] = None

    class Config:
        from_attributes = True

# Grade Schemas
class GradeUpdate(BaseModel):
    student_id: int
    course_id: int
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    note: Optional[str] = None

class GradeResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    student_code: Optional[str] = None
    course_id: int
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    credits: Optional[int] = 3
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    total_score: Optional[float] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True
