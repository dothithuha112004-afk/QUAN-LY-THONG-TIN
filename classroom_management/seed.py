from datetime import date
from classroom_management.database import engine, Base, SessionLocal
from classroom_management.models import User, Course, Schedule, Enrollment, Attendance, Grade
from classroom_management.auth import hash_password

def seed_database():
    """Initializes tables and seeds demo data into database."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing_students_count = db.query(User).filter(User.role == "student").count()
    admin_exists = db.query(User).filter(User.username == "admin").first()

    if admin_exists and existing_students_count >= 20:
        print(" Database already initialized with seed data.")
        db.close()
        return

    print(" Seeding missing initial demo data into database...")


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

    students_raw = [
        {"username": "hocsinh1", "full_name": "Lê Hoàng Nam", "email": "nam.lh@sinhvien.edu.vn", "phone": "0934567890", "age": 20, "title": "Sinh viên K65", "department": "Công nghệ thông tin", "code": "SV001"},
        {"username": "hocsinh2", "full_name": "Phạm Mai Anh", "email": "anh.pm@sinhvien.edu.vn", "phone": "0945678901", "age": 19, "title": "Sinh viên K66", "department": "Khoa Hóa & Sinh", "code": "SV002"},
        {"username": "hocsinh3", "full_name": "Đỗ Minh Trí", "email": "tri.dm@sinhvien.edu.vn", "phone": "0956789012", "age": 21, "title": "Sinh viên K64", "department": "Công nghệ thông tin", "code": "SV003"},
        {"username": "hocsinh4", "full_name": "Nguyễn Thị Thu Hà", "email": "ha.ntt@sinhvien.edu.vn", "phone": "0961234567", "age": 20, "title": "Sinh viên K65", "department": "Công nghệ thông tin", "code": "SV004"},
        {"username": "hocsinh5", "full_name": "Trần Văn Khánh", "email": "khanh.tv@sinhvien.edu.vn", "phone": "0972345678", "age": 19, "title": "Sinh viên K66", "department": "Kinh tế & Quản trị", "code": "SV005"},
        {"username": "hocsinh6", "full_name": "Vũ Hoàng Bảo", "email": "bao.vh@sinhvien.edu.vn", "phone": "0983456789", "age": 20, "title": "Sinh viên K65", "department": "Điện - Điện tử", "code": "SV006"},
        {"username": "hocsinh7", "full_name": "Bùi Thiện Nhân", "email": "nhan.bt@sinhvien.edu.vn", "phone": "0914567890", "age": 22, "title": "Sinh viên K63", "department": "Công nghệ thông tin", "code": "SV007"},
        {"username": "hocsinh8", "full_name": "Đặng Ngọc Linh", "email": "linh.dn@sinhvien.edu.vn", "phone": "0925678901", "age": 19, "title": "Sinh viên K66", "department": "Ngoại ngữ", "code": "SV008"},
        {"username": "hocsinh9", "full_name": "Hoàng Quang Huy", "email": "huy.hq@sinhvien.edu.vn", "phone": "0936789012", "age": 21, "title": "Sinh viên K64", "department": "Công nghệ thông tin", "code": "SV009"},
        {"username": "hocsinh10", "full_name": "Phan Thị Thanh Thảo", "email": "thao.ptt@sinhvien.edu.vn", "phone": "0947890123", "age": 20, "title": "Sinh viên K65", "department": "Khoa Hóa & Sinh", "code": "SV010"},
        {"username": "hocsinh11", "full_name": "Ngô Tuấn Anh", "email": "anh.nt@sinhvien.edu.vn", "phone": "0958901234", "age": 19, "title": "Sinh viên K66", "department": "Kinh tế & Quản trị", "code": "SV011"},
        {"username": "hocsinh12", "full_name": "Dương Thùy Trang", "email": "trang.dt@sinhvien.edu.vn", "phone": "0969012345", "age": 20, "title": "Sinh viên K65", "department": "Ngoại ngữ", "code": "SV012"},
        {"username": "hocsinh13", "full_name": "Nguyễn Đức Thắng", "email": "thang.nd@sinhvien.edu.vn", "phone": "0970123456", "age": 21, "title": "Sinh viên K64", "department": "Điện - Điện tử", "code": "SV013"},
        {"username": "hocsinh14", "full_name": "Lý Mỹ Duyên", "email": "duyen.lm@sinhvien.edu.vn", "phone": "0981234567", "age": 19, "title": "Sinh viên K66", "department": "Khoa Hóa & Sinh", "code": "SV014"},
        {"username": "hocsinh15", "full_name": "Hồ Thanh Tùng", "email": "tung.ht@sinhvien.edu.vn", "phone": "0912345670", "age": 22, "title": "Sinh viên K63", "department": "Công nghệ thông tin", "code": "SV015"},
        {"username": "hocsinh16", "full_name": "Trịnh Ngọc Ánh", "email": "anh.tn@sinhvien.edu.vn", "phone": "0923456701", "age": 20, "title": "Sinh viên K65", "department": "Kinh tế & Quản trị", "code": "SV016"},
        {"username": "hocsinh17", "full_name": "Võ Văn Minh", "email": "minh.vv@sinhvien.edu.vn", "phone": "0934567012", "age": 21, "title": "Sinh viên K64", "department": "Công nghệ thông tin", "code": "SV017"},
        {"username": "hocsinh18", "full_name": "Nguyễn Phương Thảo", "email": "thao.np@sinhvien.edu.vn", "phone": "0945670123", "age": 19, "title": "Sinh viên K66", "department": "Ngoại ngữ", "code": "SV018"},
        {"username": "hocsinh19", "full_name": "Đào Nhật Hoàng", "email": "hoang.dn@sinhvien.edu.vn", "phone": "0956701234", "age": 20, "title": "Sinh viên K65", "department": "Điện - Điện tử", "code": "SV019"},
        {"username": "hocsinh20", "full_name": "Lê Gia Bảo", "email": "bao.lg@sinhvien.edu.vn", "phone": "0967012345", "age": 20, "title": "Sinh viên K65", "department": "Công nghệ thông tin", "code": "SV020"},
        {"username": "thuha112004", "full_name": "Đỗ Thị Thu Hà", "email": "dothithuha112004@gmail.com", "phone": "0988888888", "age": 20, "title": "Sinh viên K65", "department": "Công nghệ thông tin", "code": "SV11"}
    ]

    new_users = []
    if not admin_exists:
        new_users.extend([admin_user, teacher1, teacher2])

    existing_usernames = {u[0] for u in db.query(User.username).all()}
    for s in students_raw:
        if s["username"] not in existing_usernames:
            new_users.append(
                User(
                    username=s["username"],
                    password_hash=default_pwd_hash,
                    role="student",
                    full_name=s["full_name"],
                    email=s["email"],
                    phone=s["phone"],
                    age=s["age"],
                    title=s["title"],
                    department=s["department"],
                    code=s["code"]
                )
            )

    if new_users:
        db.add_all(new_users)
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

    existing_courses = db.query(Course).count()
    if existing_courses == 0:
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

    existing_schedules = db.query(Schedule).count()
    if existing_schedules == 0:
        db.add_all([sched1, sched2, sched3])
        db.commit()

    # Fetch all student objects for enrollment & attendance
    student_objects = db.query(User).filter(User.role == "student").all()

    existing_enrollments = db.query(Enrollment).count()
    if existing_enrollments == 0 and student_objects:
        enrollments = []
        for idx, st in enumerate(student_objects):
            target_course = course1 if idx % 3 == 0 else (course2 if idx % 3 == 1 else course3)
            enrollments.append(Enrollment(student_id=st.id, course_id=target_course.id, term="Học kỳ 1 - 2026"))

        db.add_all(enrollments)
        db.commit()

    existing_attendance = db.query(Attendance).count()
    if existing_attendance == 0 and len(student_objects) >= 3:
        att1 = Attendance(
            schedule_id=sched1.id,
            student_id=student_objects[0].id,
            attendance_date=date(2026, 9, 21),
            status="Có mặt",
            note="Đi đúng giờ"
        )
        att2 = Attendance(
            schedule_id=sched1.id,
            student_id=student_objects[2].id,
            attendance_date=date(2026, 9, 21),
            status="Đi muộn",
            note="Trễ 15 phút"
        )
        db.add_all([att1, att2])
        db.commit()

    existing_grades = db.query(Grade).count()
    if existing_grades == 0 and len(student_objects) >= 2:
        g1 = Grade(
            student_id=student_objects[0].id,
            course_id=course1.id,
            midterm_score=8.5,
            final_score=9.0,
            total_score=8.85,
            note="Học tập xuất sắc",
            graded_by_teacher_id=teacher1.id
        )

        g2 = Grade(
            student_id=student_objects[1].id,
            course_id=course3.id,
            midterm_score=9.0,
            final_score=9.5,
            total_score=9.35,
            note="Thực hành thí nghiệm xuất sắc",
            graded_by_teacher_id=teacher2.id
        )

        db.add_all([g1, g2])
        db.commit()

    db.close()
    print(" Demo data with 21 students seeded successfully!")

if __name__ == "__main__":
    seed_database()

