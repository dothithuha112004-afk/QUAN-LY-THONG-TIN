from datetime import date
from classroom_management.database import engine, Base, SessionLocal
from classroom_management.models import User, Course, Schedule, Enrollment, Attendance, Grade
from classroom_management.auth import hash_password

def seed_database():
    """Initializes tables and seeds demo data into database."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_students_count = db.query(User).filter(User.role == "student").count()
        admin_exists = db.query(User).filter(User.username == "admin").first()

        print(" Seeding missing initial demo data into database...")

        default_pwd_hash = hash_password("password123")

        if not admin_exists:
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
            db.add_all([admin_user, teacher1, teacher2])
            db.commit()

        students_raw = [
            {"username": "hocsinh1", "full_name": "Bùi Hoàng Phương Anh", "email": "anh.bhp@sinhvien.edu.vn", "phone": "0934567890", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222503004"},
            {"username": "hocsinh2", "full_name": "Trần Bảo Anh", "email": "anh.tb@sinhvien.edu.vn", "phone": "0945678901", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Khoa Hóa & Sinh", "code": "222503022"},
            {"username": "hocsinh3", "full_name": "Vũ Tiến Duy", "email": "duy.vt@sinhvien.edu.vn", "phone": "0956789012", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222533064"},
            {"username": "hocsinh4", "full_name": "Nguyễn Nhật Ánh Dương", "email": "duong.nna@sinhvien.edu.vn", "phone": "0961234567", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222533068"},
            {"username": "hocsinh5", "full_name": "Ngô Văn Đạt", "email": "dat.nv@sinhvien.edu.vn", "phone": "0972345678", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Kinh tế & Quản trị", "code": "222533077"},
            {"username": "hocsinh6", "full_name": "Đỗ Hải Đăng", "email": "dang.dh@sinhvien.edu.vn", "phone": "0983456789", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Điện - Điện tử", "code": "222533085"},
            {"username": "hocsinh7", "full_name": "Nguyễn Đức Độ", "email": "do.nd@sinhvien.edu.vn", "phone": "0914567890", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222533090"},
            {"username": "hocsinh8", "full_name": "Đoàn Anh Đức", "email": "duc.da@sinhvien.edu.vn", "phone": "0925678901", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Ngoại ngữ", "code": "222533094"},
            {"username": "hocsinh9", "full_name": "Đào Duy Đường", "email": "duong.dd@sinhvien.edu.vn", "phone": "0936789012", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222533099"},
            {"username": "hocsinh10", "full_name": "Đỗ Thị Thu Hà", "email": "ha.dtt@sinhvien.edu.vn", "phone": "0947890123", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Khoa Hóa & Sinh", "code": "222533106"},
            {"username": "hocsinh11", "full_name": "Trần Trung Hiếu", "email": "hieu.tt@sinhvien.edu.vn", "phone": "0958901234", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Kinh tế & Quản trị", "code": "222533123"},
            {"username": "hocsinh12", "full_name": "Nguyễn Quang Hưng", "email": "hung.nq@sinhvien.edu.vn", "phone": "0969012345", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Ngoại ngữ", "code": "212511851"},
            {"username": "hocsinh13", "full_name": "Nguyễn Đăng Hướng", "email": "huong.nd@sinhvien.edu.vn", "phone": "0970123456", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Điện - Điện tử", "code": "222533153"},
            {"username": "hocsinh14", "full_name": "Nguyễn Phương Linh", "email": "linh.np@sinhvien.edu.vn", "phone": "0981234567", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Khoa Hóa & Sinh", "code": "222533177"},
            {"username": "hocsinh15", "full_name": "Đỗ Hải Long", "email": "long.dh@sinhvien.edu.vn", "phone": "0912345670", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222503181"},
            {"username": "hocsinh16", "full_name": "Đào Duy Mạnh", "email": "manh.dd@sinhvien.edu.vn", "phone": "0923456701", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Kinh tế & Quản trị", "code": "222533189"},
            {"username": "hocsinh17", "full_name": "Kiều Tuấn Nam", "email": "nam.kt@sinhvien.edu.vn", "phone": "0934567012", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222503204"},
            {"username": "hocsinh18", "full_name": "Nguyễn Thị Hồng Ngọc", "email": "ngoc.nth@sinhvien.edu.vn", "phone": "0945670123", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Ngoại ngữ", "code": "222533219"},
            {"username": "hocsinh19", "full_name": "Đỗ Anh Phương", "email": "phuong.da@sinhvien.edu.vn", "phone": "0956701234", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Điện - Điện tử", "code": "222503229"},
            {"username": "hocsinh20", "full_name": "Ngô Hải Quân", "email": "quan.nh@sinhvien.edu.vn", "phone": "0967012345", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222503241"},
            {"username": "thuha112004", "full_name": "Nguyễn Minh Quân", "email": "quan.nm@sinhvien.edu.vn", "phone": "0988888888", "age": 22, "title": "Kết cấu xây dựng K63", "department": "Công nghệ thông tin", "code": "222533242"}
        ]

        for s in students_raw:
            user = db.query(User).filter(User.username == s["username"]).first()
            if user:
                user.full_name = s["full_name"]
                user.code = s["code"]
                user.title = s["title"]
                user.age = s["age"]
            else:
                db.add(
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
        db.commit()

        # Seed courses safely
        c1 = db.query(Course).filter(Course.course_code == "INT1001").first()
        if not c1:
            c1 = Course(
                course_code="INT1001",
                course_name="Lập trình Python Căn Bản",
                credits=3,
                department="Công nghệ thông tin",
                description="Môn học nhập môn lập trình Python, xử lý dữ liệu và xây dựng ứng dụng web.",
                term="Học kỳ 1 - 2026"
            )
            db.add(c1)
            db.commit()
            db.refresh(c1)

        c2 = db.query(Course).filter(Course.course_code == "INT2004").first()
        if not c2:
            c2 = Course(
                course_code="INT2004",
                course_name="Cơ sở dữ liệu SQL Server",
                credits=4,
                department="Công nghệ thông tin",
                description="Kiến thức thiết kế CSDL quan hệ, truy vấn T-SQL và quản lý dữ liệu.",
                term="Học kỳ 1 - 2026"
            )
            db.add(c2)
            db.commit()
            db.refresh(c2)

        c3 = db.query(Course).filter(Course.course_code == "BIO1002").first()
        if not c3:
            c3 = Course(
                course_code="BIO1002",
                course_name="Sinh học Đại Cương",
                credits=3,
                department="Khoa Hóa & Sinh",
                description="Các nguyên lý cơ bản của sinh học tế bào và di truyền.",
                term="Học kỳ 1 - 2026"
            )
            db.add(c3)
            db.commit()
            db.refresh(c3)

        teacher1 = db.query(User).filter(User.role == "teacher").first()
        teacher2 = db.query(User).filter(User.role == "teacher").offset(1).first() or teacher1

        # Seed schedules safely
        if db.query(Schedule).count() == 0 and teacher1 and c1:
            sched1 = Schedule(
                course_id=c1.id,
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
                course_id=c2.id if c2 else c1.id,
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
                course_id=c3.id if c3 else c1.id,
                teacher_id=teacher2.id if teacher2 else teacher1.id,
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

        # Seed enrollments safely
        student_objects = db.query(User).filter(User.role == "student").all()
        courses = [c for c in [c1, c2, c3] if c is not None]

        if db.query(Enrollment).count() == 0 and student_objects and courses:
            enrollments = []
            for idx, st in enumerate(student_objects):
                target_course = courses[idx % len(courses)]
                enrollments.append(Enrollment(student_id=st.id, course_id=target_course.id, term="Học kỳ 1 - 2026"))
            db.add_all(enrollments)
            db.commit()

        print(" Demo data with 21 real students updated successfully!")
    except Exception as e:
        print(f"Seed error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
