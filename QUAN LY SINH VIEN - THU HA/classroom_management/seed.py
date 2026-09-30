from datetime import date
from classroom_management.database import engine, Base, SessionLocal
from classroom_management.models import User, Course, Schedule, Enrollment, Attendance, Grade
from classroom_management.auth import hash_password

def seed_database():
    """Initializes tables and seeds demo data into database."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).filter(User.username == "admin").first():
        print(" Database already initialized with seed data.")
        db.close()
        return

    print(" Seeding initial demo data into database...")

    default_pwd_hash = hash_password("password123")

    admin_user = User(
        username="admin",
        password_hash=default_pwd_hash,
        role="admin",
        full_name="Quản Trị Viên Hệ Thống",
        email="admin@truonghoc.edu.vn",
        phone="0901234567",
        age=35,
        title="Quản Trị Viên",
        department="Phòng Đào Tạo",
        code="ADM001"
    )

    teacher1 = User(
        username="giaovien1",
        password_hash=default_pwd_hash,
        role="teacher",
        full_name="ThS. Nguyễn Văn Thắng",
        email="thang.nv@truonghoc.edu.vn",
        phone="0912345678",
        age=40,
        title="Giảng viên chính",
        department="Công nghệ thông tin",
        code="GV001"
    )

    teacher2 = User(
        username="giaovien2",
        password_hash=default_pwd_hash,
        role="teacher",
        full_name="TS. Trần Thị Hương",
        email="huong.tt@truonghoc.edu.vn",
        phone="0923456789",
        age=38,
        title="Phó Trưởng bộ môn",
        department="Khoa Hóa & Sinh",
        code="GV002"
    )

    student1 = User(
        username="hocsinh1",
        password_hash=default_pwd_hash,
        role="student",
        full_name="Lê Hoàng Nam",
        email="nam.lh@sinhvien.edu.vn",
        phone="0934567890",
        age=20,
        title="Sinh viên K65",
        department="Công nghệ thông tin",
        code="SV001"
    )

    student2 = User(
        username="hocsinh2",
        password_hash=default_pwd_hash,
        role="student",
        full_name="Phạm Mai Anh",
        email="anh.pm@sinhvien.edu.vn",
        phone="0945678901",
        age=19,
        title="Sinh viên K66",
        department="Khoa Hóa & Sinh",
        code="SV002"
    )

    student3 = User(
        username="hocsinh3",
        password_hash=default_pwd_hash,
        role="student",
        full_name="Đỗ Minh Trí",
        email="tri.dm@sinhvien.edu.vn",
        phone="0956789012",
        age=21,
        title="Sinh viên K64",
        department="Công nghệ thông tin",
        code="SV003"
    )

    db.add_all([admin_user, teacher1, teacher2, student1, student2, student3])
    db.commit()

    course1 = Course(
        course_code="INT1001",
        course_name="Lập trình Python Căn Bản",
        credits=3,
        department="Công nghệ thông tin",
        description="Môn học nhập môn lập trình Python, xử lý dữ liệu và xây dựng ứng dụng web.",
        term="Học kỳ 1 - 2026"
    )

    course2 = Course(
        course_code="INT2004",
        course_name="Cơ sở dữ liệu SQL Server",
        credits=4,
        department="Công nghệ thông tin",
        description="Kiến thức thiết kế CSDL quan hệ, truy vấn T-SQL và quản lý dữ liệu.",
        term="Học kỳ 1 - 2026"
    )

    course3 = Course(
        course_code="BIO1002",
        course_name="Sinh học Đại Cương",
        credits=3,
        department="Khoa Hóa & Sinh",
        description="Các nguyên lý cơ bản của sinh học tế bào và di truyền.",
        term="Học kỳ 1 - 2026"
    )

    db.add_all([course1, course2, course3])
    db.commit()

    sched1 = Schedule(
        course_id=course1.id,
        teacher_id=teacher1.id,
        room="Phòng 301 - A2",
        day_of_week="Thứ Hai",
        start_time="07:30",
        end_time="10:30",
        week_number=1,
        month_number=9,
        term="Học kỳ 1 - 2026"
    )

    sched2 = Schedule(
        course_id=course2.id,
        teacher_id=teacher1.id,
        room="Phòng Lab 2 - B1",
        day_of_week="Thứ Tư",
        start_time="13:30",
        end_time="16:30",
        week_number=1,
        month_number=9,
        term="Học kỳ 1 - 2026"
    )

    sched3 = Schedule(
        course_id=course3.id,
        teacher_id=teacher2.id,
        room="Phòng 102 - C3",
        day_of_week="Thứ Sáu",
        start_time="08:00",
        end_time="11:00",
        week_number=1,
        month_number=9,
        term="Học kỳ 1 - 2026"
    )

    db.add_all([sched1, sched2, sched3])
    db.commit()

    en1 = Enrollment(student_id=student1.id, course_id=course1.id, term="Học kỳ 1 - 2026")
    en2 = Enrollment(student_id=student1.id, course_id=course2.id, term="Học kỳ 1 - 2026")
    en3 = Enrollment(student_id=student2.id, course_id=course3.id, term="Học kỳ 1 - 2026")
    en4 = Enrollment(student_id=student3.id, course_id=course1.id, term="Học kỳ 1 - 2026")

    db.add_all([en1, en2, en3, en4])
    db.commit()

    att1 = Attendance(
        schedule_id=sched1.id,
        student_id=student1.id,
        attendance_date=date(2026, 9, 21),
        status="Có mặt",
        note="Đi đúng giờ"
    )
    att2 = Attendance(
        schedule_id=sched1.id,
        student_id=student3.id,
        attendance_date=date(2026, 9, 21),
        status="Đi muộn",
        note="Trễ 15 phút"
    )

    db.add_all([att1, att2])
    db.commit()

    g1 = Grade(
        student_id=student1.id,
        course_id=course1.id,
        midterm_score=8.5,
        final_score=9.0,
        total_score=8.85,
        note="Học tập xuất sắc",
        graded_by_teacher_id=teacher1.id
    )

    g2 = Grade(
        student_id=student1.id,
        course_id=course2.id,
        midterm_score=7.5,
        final_score=8.0,
        total_score=7.8,
        note="Tích cực tham gia xây dựng bài",
        graded_by_teacher_id=teacher1.id
    )

    g3 = Grade(
        student_id=student2.id,
        course_id=course3.id,
        midterm_score=9.0,
        final_score=9.5,
        total_score=9.35,
        note="Thực hành thí nghiệm xuất sắc",
        graded_by_teacher_id=teacher2.id
    )

    db.add_all([g1, g2, g3])
    db.commit()

    db.close()
    print(" Demo data seeded successfully!")

if __name__ == "__main__":
    seed_database()
