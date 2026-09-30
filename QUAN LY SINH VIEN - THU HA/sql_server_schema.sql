-- =================================================================
-- SCRIPT TẠO DATABASE VÀ BẢNG CHO QUẢN LÝ LỚP HỌC (SQL SERVER)
-- =================================================================

-- 1. Tạo Database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = N'ClassroomDB')
BEGIN
    CREATE DATABASE ClassroomDB;
END
GO

USE ClassroomDB;
GO

-- 2. Xóa các bảng nếu đã tồn tại (Để reset khi cần)
IF OBJECT_ID('dbo.attendances', 'U') IS NOT NULL DROP TABLE dbo.attendances;
IF OBJECT_ID('dbo.grades', 'U') IS NOT NULL DROP TABLE dbo.grades;
IF OBJECT_ID('dbo.schedules', 'U') IS NOT NULL DROP TABLE dbo.schedules;
IF OBJECT_ID('dbo.enrollments', 'U') IS NOT NULL DROP TABLE dbo.enrollments;
IF OBJECT_ID('dbo.courses', 'U') IS NOT NULL DROP TABLE dbo.courses;
IF OBJECT_ID('dbo.users', 'U') IS NOT NULL DROP TABLE dbo.users;
GO

-- 3. Bảng Người Dùng (users) - Giáo viên, Sinh viên, Admin
CREATE TABLE dbo.users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
    full_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NULL,
    phone NVARCHAR(20) NULL,
    age INT NULL,
    title NVARCHAR(50) NULL, -- Chức vị (Ví dụ: Giảng viên chính, Trưởng bộ môn, Sinh viên khóa 20)
    department NVARCHAR(100) NULL, -- Bộ môn / Khoa (Ví dụ: Công nghệ thông tin, Toán ứng dụng)
    code NVARCHAR(50) NULL, -- Mã GV (GV001) hoặc Mã SV (SV001)
    avatar_url NVARCHAR(255) NULL,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 4. Bảng Môn Học (courses)
CREATE TABLE dbo.courses (
    id INT IDENTITY(1,1) PRIMARY KEY,
    course_code NVARCHAR(20) NOT NULL UNIQUE,
    course_name NVARCHAR(100) NOT NULL,
    credits INT NOT NULL DEFAULT 3,
    department NVARCHAR(100) NULL,
    description NVARCHAR(MAX) NULL,
    term NVARCHAR(20) NOT NULL DEFAULT N'Học kỳ 1 - 2026',
    tuition_fee FLOAT NOT NULL DEFAULT 1500000.0 -- Học phí (VNĐ/tín chỉ)
);
GO

-- 5. Bảng Đăng Ký Môn Học (enrollments)
CREATE TABLE dbo.enrollments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,
    course_id INT NOT NULL FOREIGN KEY REFERENCES dbo.courses(id) ON DELETE CASCADE,
    term NVARCHAR(20) NOT NULL,
    enrolled_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_Student_Course_Term UNIQUE(student_id, course_id, term)
);
GO

-- 6. Bảng Lịch Học / Lịch Dạy (schedules)
CREATE TABLE dbo.schedules (
    id INT IDENTITY(1,1) PRIMARY KEY,
    course_id INT NOT NULL FOREIGN KEY REFERENCES dbo.courses(id) ON DELETE CASCADE,
    teacher_id INT NOT NULL FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,
    room NVARCHAR(50) NOT NULL,
    day_of_week NVARCHAR(20) NOT NULL, -- Thứ Hai, Thứ Ba, ...
    start_time NVARCHAR(10) NOT NULL, -- 07:30
    end_time NVARCHAR(10) NOT NULL, -- 10:30
    week_number INT NOT NULL, -- Tuần 1 đến 16
    month_number INT NOT NULL, -- Tháng 1 đến 12
    term NVARCHAR(20) NOT NULL
);
GO

-- 7. Bảng Điểm Danh (attendances)
CREATE TABLE dbo.attendances (
    id INT IDENTITY(1,1) PRIMARY KEY,
    schedule_id INT NOT NULL FOREIGN KEY REFERENCES dbo.schedules(id) ON DELETE CASCADE,
    student_id INT NOT NULL FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    status NVARCHAR(20) NOT NULL CHECK (status IN (N'Có mặt', N'Vắng mặt', N'Đi muộn', N'Có phép')),
    note NVARCHAR(255) NULL,
    recorded_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_Schedule_Student_Date UNIQUE(schedule_id, student_id, attendance_date)
);
GO

-- 8. Bảng Điểm Số (grades)
CREATE TABLE dbo.grades (
    id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,
    course_id INT NOT NULL FOREIGN KEY REFERENCES dbo.courses(id) ON DELETE CASCADE,
    midterm_score FLOAT NULL, -- Điểm giữa kỳ
    final_score FLOAT NULL, -- Điểm cuối kỳ
    total_score FLOAT NULL, -- Điểm tổng kết
    note NVARCHAR(255) NULL,
    graded_by_teacher_id INT NULL FOREIGN KEY REFERENCES dbo.users(id),
    updated_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_Student_Course_Grade UNIQUE(student_id, course_id)
);
GO

-- 9. Dữ Liệu Mẫu Ban Đầu (Initial Seed Data)
-- Mật khẩu mặc định cho các tài khoản là: password123
INSERT INTO dbo.users (username, password_hash, role, full_name, email, phone, age, title, department, code)
VALUES 
(N'admin', N'$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'admin', N'Quản Trị Viên Hệ Thống', N'admin@truonghoc.edu.vn', N'0901234567', 35, N'Quản Trị Viên', N'Phòng Đào Tạo', N'ADM001'),
(N'giaovien1', N'$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'teacher', N'ThS. Nguyễn Văn Thắng', N'thang.nv@truonghoc.edu.vn', N'0912345678', 40, N'Giảng viên chính', N'Công nghệ thông tin', N'GV001'),
(N'giaovien2', N'$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'teacher', N'TS. Trần Thị Hương', N'huong.tt@truonghoc.edu.vn', N'0923456789', 38, N'Phó Trưởng bộ môn', N'Khoa Hóa & Sinh', N'GV002'),
(N'hocsinh1', N'$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'student', N'Lê Hoàng Nam', N'nam.lh@sinhvien.edu.vn', N'0934567890', 20, N'Sinh viên K65', N'Công nghệ thông tin', N'SV001'),
(N'hocsinh2', N'$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'student', N'Phạm Mai Anh', N'anh.pm@sinhvien.edu.vn', N'0945678901', 19, N'Sinh viên K66', N'Khoa Hóa & Sinh', N'SV002');

INSERT INTO dbo.courses (course_code, course_name, credits, department, description, term)
VALUES 
(N'INT1001', N'Lập trình Python Căn Bản', 3, N'Công nghệ thông tin', N'Môn học nhập môn lập trình Python, xử lý dữ liệu và xây dựng ứng dụng web.', N'Học kỳ 1 - 2026'),
(N'INT2004', N'Cơ sở dữ liệu SQL Server', 4, N'Công nghệ thông tin', N'Kiến thức thiết kế CSDL quan hệ, truy vấn T-SQL và quản lý dữ liệu.', N'Học kỳ 1 - 2026'),
(N'BIO1002', N'Sinh học Đại Cương', 3, N'Khoa Hóa & Sinh', N'Các nguyên lý cơ bản của sinh học tế bào và di truyền.', N'Học kỳ 1 - 2026');

INSERT INTO dbo.schedules (course_id, teacher_id, room, day_of_week, start_time, end_time, week_number, month_number, term)
VALUES 
(1, 2, N'Phòng 301 - A2', N'Thứ Hai', N'07:30', N'10:30', 1, 9, N'Học kỳ 1 - 2026'),
(2, 2, N'Phòng Lab 2 - B1', N'Thứ Tư', N'13:30', N'16:30', 1, 9, N'Học kỳ 1 - 2026'),
(3, 3, N'Phòng 102 - C3', N'Thứ Sáu', N'08:00', N'11:00', 1, 9, N'Học kỳ 1 - 2026');

INSERT INTO dbo.enrollments (student_id, course_id, term)
VALUES 
(4, 1, N'Học kỳ 1 - 2026'),
(4, 2, N'Học kỳ 1 - 2026'),
(5, 3, N'Học kỳ 1 - 2026');

INSERT INTO dbo.grades (student_id, course_id, midterm_score, final_score, total_score, note, graded_by_teacher_id)
VALUES 
(4, 1, 8.5, 9.0, 8.85, N'Học tập xuất sắc', 2),
(4, 2, 7.5, 8.0, 7.8, N'Tích cực làm bài tập', 2);

PRINT 'Khởi tạo dữ liệu SQL Server hoàn tất!';
GO
