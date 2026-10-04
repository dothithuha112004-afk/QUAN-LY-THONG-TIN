from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from classroom_management.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student") # admin, teacher, student
    
    # Profile fields requested by user
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    title = Column(String(50), nullable=True)        # Chức vị (Giảng viên chính, Trưởng bộ môn, SV K65...)
    department = Column(String(100), nullable=True)   # Bộ môn / Khoa (CNTT, Hóa & Sinh...)
    code = Column(String(50), nullable=True)          # Mã GV / Mã SV (GV001, SV001...)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    schedules = relationship("Schedule", back_populates="teacher", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    grades = relationship("Grade", foreign_keys="[Grade.student_id]", back_populates="student", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True, nullable=False, index=True)
    course_name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False, default=3)
    department = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    term = Column(String(20), nullable=False, default="Học kỳ 1 - 2026")
    tuition_fee = Column(Float, nullable=False, default=1500000.0) # Học phí per course / credit (VNĐ)

    # Relationships
    schedules = relationship("Schedule", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="course", cascade="all, delete-orphan")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room = Column(String(50), nullable=False)
    day_of_week = Column(String(20), nullable=False) # Thứ Hai, Thứ Ba, ...
    start_time = Column(String(10), nullable=False) # 07:30
    end_time = Column(String(10), nullable=False)   # 10:30
    week_number = Column(Integer, nullable=False, default=1)  # Tuần 1 -> 16
    month_number = Column(Integer, nullable=False, default=9) # Tháng 1 -> 12
    term = Column(String(20), nullable=False, default="Học kỳ 1 - 2026")

    # Relationships
    course = relationship("Course", back_populates="schedules")
    teacher = relationship("User", back_populates="schedules")
    attendances = relationship("Attendance", back_populates="schedule", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    term = Column(String(20), nullable=False, default="Học kỳ 1 - 2026")
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False) # Có mặt, Vắng mặt, Đi muộn, Có phép
    note = Column(String(255), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    schedule = relationship("Schedule", back_populates="attendances")
    student = relationship("User", back_populates="attendances")


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    midterm_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    note = Column(String(255), nullable=True)
    graded_by_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("User", foreign_keys=[student_id], back_populates="grades")
    course = relationship("Course", back_populates="grades")
