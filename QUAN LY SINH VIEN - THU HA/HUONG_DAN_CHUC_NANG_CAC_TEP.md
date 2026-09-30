# 📖 HƯỚNG DẪN CHỨC NĂNG CỦA TỪNG TỆP TRONG DỰ ÁN QUẢN LÝ SINH VIÊN - THU HÀ

Tài liệu này giải thích chi tiết chức năng, vai trò và nhiệm vụ của từng thư mục và tệp tin trong dự án **Hệ Thống Quản Lý Lớp Học (Classroom Management System)**.

---

## 📌 1. Các Tệp Tin Tại Thư Mục Gốc (Root Directory)

| Tệp tin / Thư mục | Chức năng & Mô tả chi tiết |
| :--- | :--- |
| **`run.py`** | Script chính để khởi chạy ứng dụng web ở môi trường Local. Sử dụng thư viện `uvicorn` để chạy server FastAPI tại địa chỉ `http://127.0.0.1:8000` với chế độ tự động reload (`reload=True`). |
| **`pyproject.toml`** | File cấu hình gói tiêu chuẩn cho dự án Python (Enterprise Package standard). Định nghĩa các thông tin metadata của dự án và cấu hình hệ thống build script. |
| **`requirements.txt`** | Danh sách các thư viện Python phụ thuộc cần thiết cho dự án như `fastapi`, `uvicorn`, `sqlalchemy`, `pyjwt`, `passlib`, `pyodbc`, `pydantic`. Dùng cho lệnh `pip install -r requirements.txt`. |
| **`sql_server_schema.sql`** | File script T-SQL chứa mã lệnh tạo cơ sở dữ liệu `ClassroomDB` cùng tất cả các bảng dữ liệu (`users`, `courses`, `schedules`, `enrollments`, `attendances`, `grades`) và dữ liệu mẫu ban đầu trên hệ quản trị CSDL **Microsoft SQL Server**. |
| **`vercel.json`** | File cấu hình dành riêng cho việc triển khai (deploy) ứng dụng web FastAPI lên nền tảng đám mây **Vercel** thông qua Serverless Functions. |
| **`.gitignore`** | File cấu hình Git nhằm loại bỏ các thư mục/tệp tin không cần thiết hoặc chứa thông tin nhạy cảm khỏi việc theo dõi mã nguồn (ví dụ: `__pycache__`, file CSDL `*.db`, môi trường ảo `.venv`, logs,...). |
| **`classroom.db`** | File cơ sở dữ liệu dạng **SQLite**. Được tạo tự động khi khởi chạy dự án local nếu hệ thống không được cấu hình kết nối tới SQL Server (chế độ fallback SQLite). |
| **`README.md`** | Tài liệu giới thiệu tổng quan dự án, hướng dẫn cài đặt, cấu hình CSDL, danh sách tài khoản demo và hướng dẫn đưa ứng dụng lên GitHub & Vercel. |

---

## 📌 2. Thư Mục `api/` (Vercel Serverless Function)

| Tệp tin | Chức năng & Mô tả chi tiết |
| :--- | :--- |
| **`api/index.py`** | Điểm đầu vào (Entrypoint) dành riêng cho dịch vụ Vercel Serverless Function. Thực hiện import ứng dụng `app` từ package `classroom_management.main` để xử lý các request HTTP trên Serverless environment. |

---

## 📌 3. Thư Mục Cốt Lõi `classroom_management/` (Backend Package)

Đây là nơi chứa toàn bộ logic Backend chính của ứng dụng theo mô hình kiến trúc 3 tầng (3-Tier Architecture):

| Tệp tin | Chức năng & Mô tả chi tiết |
| :--- | :--- |
| **`classroom_management/__init__.py`** | Khai báo thư mục `classroom_management` là một Python Package chính thức. |
| **`classroom_management/database.py`** | **Tầng Quản lý Kết nối Cơ sở Dữ liệu**: <br>• Khởi tạo SQLAlchemy Engine kết nối tới **MS SQL Server** (`mssql+pyodbc`).<br>• Tự động bắt lỗi và chuyển đổi (fallback) sang **SQLite** nếu không kết nối được SQL Server.<br>• Cung cấp `SessionLocal`, `Base` và hàm `get_db()` dependency dùng cho việc truy vấn DB trong các API routes. |
| **`classroom_management/models.py`** | **Tầng ORM Models (Data Models)**: <br>Định nghĩa ánh xạ các bảng CSDL sang đối tượng Python bao gồm:<br>• `User`: Người dùng (Admin, Giáo viên, Sinh viên).<br>• `Course`: Môn học.<br>• `Schedule`: Lịch giảng dạy & thời khóa biểu.<br>• `Enrollment`: Đăng ký môn học của sinh viên.<br>• `Attendance`: Dữ liệu điểm danh.<br>• `Grade`: Dữ liệu bảng điểm (Điểm giữa kỳ, Cuối kỳ, Tổng kết). |
| **`classroom_management/schemas.py`** | **Tầng Pydantic Schemas (Data Validation)**: <br>Định nghĩa các chuẩn chuẩn hóa và kiểm tra hợp lệ dữ liệu đầu vào/đầu ra cho các API endpoints (cho Đăng nhập, Đăng ký, Tạo tài khoản, Nhập điểm, Điểm danh, Đăng ký môn học...). |
| **`classroom_management/auth.py`** | **Tầng Bảo mật & Xác thực (Authentication & RBAC)**: <br>• Băm và kiểm tra mật khẩu an toàn với `passlib (bcrypt)`.<br>• Tạo và xác thực mã Token JWT (`JSON Web Token`).<br>• Khởi tạo các hàm dependency phân quyền người dùng: `get_current_user`, `require_admin`, `require_teacher`, `require_student`. |
| **`classroom_management/seed.py`** | **Tệp Khởi tạo Dữ liệu Mẫu (Data Seeder)**: <br>Chứa hàm `seed_database()` tự động chèn các tài khoản Admin, Giáo viên, Sinh viên mặc định cùng dữ liệu môn học, lịch dạy, điểm danh và bảng điểm ban đầu vào CSDL khi khởi chạy lần đầu. |
| **`classroom_management/main.py`** | **Tệp Khởi tạo Ứng dụng FastAPI (App Factory)**: <br>• Gọi lệnh tạo bảng CSDL và seed dữ liệu mẫu.<br>• Gắn các Router API từ thư mục `routers/`.<br>• Mount thư mục tệp tĩnh `/static`.<br>• Phục vụ route trang chủ `/` trả về giao diện `index.html`. |

---

## 📌 4. Thư Mục `classroom_management/routers/` (Tầng API Endpoints)

Thư mục chứa mã nguồn xử lý logic theo từng phân hệ người dùng (Role-Based Endpoints):

| Tệp tin | Chức năng & Mô tả chi tiết |
| :--- | :--- |
| **`routers/__init__.py`** | Đánh dấu thư mục `routers` là một Python Sub-package. |
| **`routers/auth_router.py`** | **Router Xác thực Người dùng**: <br>• `/api/auth/login`: Đăng nhập hệ thống, cấp JWT Token.<br>• `/api/auth/me`: Lấy thông tin hồ sơ người dùng đang đăng nhập.<br>• `/api/auth/profile`: Cập nhật thông tin cá nhân.<br>• `/api/auth/change-password`: Đổi mật khẩu tài khoản. |
| **`routers/admin_router.py`** | **Router Quản trị Viên (Admin)**: <br>• Quản lý tài khoản (Xem danh sách, Tạo tài khoản mới, Thay đổi phân quyền Admin/Teacher/Student).<br>• Quản lý danh mục Môn học (Tạo môn học, sửa thông tin).<br>• Phân công Xếp lịch giảng dạy cho Giáo viên.<br>• Thống kê tổng quan số lượng Giáo viên, Sinh viên, Môn học. |
| **`routers/teacher_router.py`** | **Router Phân hệ Giáo viên (Teacher)**: <br>• Xem lịch giảng dạy cá nhân (theo Tuần / Tháng).<br>• Xem danh sách sinh viên theo lớp môn học phụ trách.<br>• Thực hiện điểm danh sinh viên (Có mặt, Vắng mặt, Đi muộn, Có phép).<br>• Nhập và chỉnh sửa điểm số sinh viên (Điểm giữa kỳ 40%, Cuối kỳ 60%, Tự động tính tổng kết). |
| **`routers/student_router.py`** | **Router Phân hệ Sinh viên (Student)**: <br>• Tra cứu danh sách môn học mở và Đăng ký / Hủy đăng ký môn học.<br>• Xem lịch học cá nhân các môn đã đăng ký.<br>• Xem kết quả điểm danh cá nhân từng buổi học.<br>• Tra cứu bảng điểm cá nhân chi tiết từng môn. |

---

## 📌 5. Thư Mục `classroom_management/templates/` & `static/` (Tầng Frontend UI)

| Thư mục / Tệp tin | Chức năng & Mô tả chi tiết |
| :--- | :--- |
| **`templates/index.html`** | **Giao diện Dashboard Single Page Application (SPA)**: <br>Chứa toàn bộ cấu trúc HTML của ứng dụng theo phong cách thiết kế **Glassmorphism modern**. Giao diện tự động thay đổi các Menu, Sidebar, Card và Bảng dữ liệu tương ứng với quyền đăng nhập của đối tượng (Admin, Giáo viên, Sinh viên). |
| **`static/css/style.css`** | **Tệp Định dạng Giao diện (Custom CSS)**: <br>Chứa định nghĩa CSS variables, hiệu ứng Glassmorphism (làm mờ kính, viền phát sáng), layout flex/grid responsive, style cho bảng biểu, modal popup, toast alert notification và các nút bấm tương tác. |
| **`static/js/app.js`** | **Tệp Xử lý Logic Giao diện Frontend (JavaScript Vanilla)**: <br>• Quản lý trạng thái đăng nhập, lưu trữ Token JWT trong `localStorage`.<br>• Gọi API Backend (Fetch API) để thực hiện các thao tác Đăng nhập, Đăng ký môn học, Điểm danh, Nhập điểm, Quản lý tài khoản.<br>• Rendering động giao diện HTML theo vai trò người dùng và hiển thị thông báo phản hồi (Notifications). |

---

## 💡 Tóm Tắt Luồng Hoạt Động (Architecture Flow)

1. Khi người dùng chạy `python run.py`, server `uvicorn` sẽ load ứng dụng FastAPI từ `classroom_management/main.py`.
2. `main.py` kết nối cơ sở dữ liệu qua `database.py` (SQL Server hoặc fallback SQLite), tự tạo bảng từ `models.py` và nạp dữ liệu mẫu từ `seed.py`.
3. Trình duyệt truy cập `http://127.0.0.1:8000/`, `main.py` trả về giao diện Single Page `index.html`.
4. Người dùng thao tác trên giao diện, file `static/js/app.js` gửi các Yêu cầu (HTTP Requests) chứa JWT Token tới các Endpoint API trong `routers/`.
5. Các Router kiểm tra quyền qua `auth.py`, kiểm soát dữ liệu qua `schemas.py`, truy vấn và cập nhật CSDL qua `models.py` và trả về phản hồi JSON cho Frontend hiển thị.
