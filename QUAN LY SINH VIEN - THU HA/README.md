<<<<<<< HEAD
# 🎓 Hệ Thống Quản Lý Lớp Học (Classroom Management System)

Dự án mô hình **3 Tầng (3-Tier Architecture)** được phát triển bằng ngôn ngữ **Python (FastAPI)** kết hợp giao diện **Glassmorphism Web Dashboard**, hỗ trợ **SQL Server** làm tầng dữ liệu và sẵn sàng deploy lên **Vercel**.

---

## 📌 Kiến Trúc Dự Án (Project Layout Standard)

```text
Managerment_of_class/
├── classroom_management/          # Core Python Enterprise Package
│   ├── __init__.py
│   ├── main.py                    # FastAPI Application Factory
│   ├── database.py                # Kết nối CSDL SQL Server & SQLite Fallback
│   ├── models.py                  # SQLAlchemy ORM Data Models
│   ├── schemas.py                 # Pydantic Schemas Validation
│   ├── auth.py                    # JWT Authentication & Phân quyền RBAC
│   ├── seed.py                    # Tạo dữ liệu mẫu ban đầu
│   ├── routers/                   # API Endpoints chia theo tầng/chức năng
│   │   ├── auth_router.py         # Đăng nhập, Đăng xuất, Profile
│   │   ├── admin_router.py        # Tạo tài khoản, phân quyền, môn học, lịch dạy
│   │   ├── teacher_router.py      # Lịch dạy, danh sách học sinh, điểm danh, cho điểm
│   │   └── student_router.py      # Đăng ký môn học, lịch học, bảng điểm cá nhân
│   ├── static/                    # Giao diện Frontend UI (CSS & JS)
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/                 # Single Page Dashboard Interface
│       └── index.html
├── api/
│   └── index.py                   # Vercel Serverless Entrypoint
├── sql_server_schema.sql          # T-SQL Script tạo CSDL & Bảng trên MS SQL Server
├── run.py                         # File chạy dự án local (python run.py)
├── pyproject.toml                 # Cấu hình chuẩn Python Enterprise Package
├── requirements.txt               # Thư viện phụ thuộc
├── vercel.json                    # Cấu hình Deploy Vercel
├── .gitignore
└── README.md
```

---

## 🔑 Cấu Hình Phân Quyền 3 Đối Tượng (Role-Based Access Control)

### 1. 👨‍🏫 Giáo Viên (Teacher)
- **Danh sách hồ sơ học sinh**: Xem thông tin chi tiết hồ sơ các sinh viên (Họ tên, mã SV, chức vị/lớp, bộ môn, SĐT, email).
- **Lịch dạy tuần & tháng**: Xem thời khóa biểu các lớp mình phụ trách theo từng tuần và từng tháng.
- **Chỉnh sửa hồ sơ cá nhân**: Cập nhật Họ và tên, Chức vị (Giảng viên chính, Trưởng bộ môn...), Tuổi, Bộ môn/Khoa, Email, SĐT.
- **Điểm danh học sinh**: Chọn lịch dạy & ngày để cập nhật trạng thái `Có mặt`, `Vắng mặt`, `Đi muộn`, `Có phép` kèm ghi chú lý do.
- **Cho điểm sinh viên**: Nhập và chỉnh sửa điểm Giữa kỳ (40%), Cuối kỳ (60%) cho từng môn dạy. Hệ thống tự động tính điểm Tổng kết.

### 2. 🎓 Sinh Viên / Học Sinh (Student)
- **Đăng ký môn học**: Xem danh sách môn học mở trong học kỳ và thực hiện Đăng ký / Hủy đăng ký chỉ với 1 click.
- **Chỉnh sửa hồ sơ cá nhân**: Cập nhật thông tin thông tin cá nhân.
- **Xem lịch học**: Xem thời khóa biểu cá nhân các môn đã đăng ký theo từng tuần và tháng.
- **Xem bảng điểm & Điểm danh**: Tra cứu điểm số từng môn học và lịch sử điểm danh cá nhân.

### 3. 🔑 Quản Trị Viên (Admin)
- Thừa hưởng **tất cả quyền** của Giáo viên và Sinh viên.
- **Tạo tài khoản & Phân quyền**: Tạo tài khoản mới, gán/thay đổi quyền (role) linh hoạt giữa `Admin`, `Teacher`, `Student`.
- **Quản lý môn học & Xếp lịch dạy**: Tạo môn học mới, xếp lịch giảng dạy cho giáo viên.
- **Thống kê hệ thống**: Tổng số Giáo viên, Sinh viên, Môn học và Lớp học.

---

## ⚡ Hướng Dẫn Khởi Chạy Local

### 1. Cài Đặt Thư Viện
```bash
pip install -r requirements.txt
```

### 2. Khởi Chạy Server
```bash
python run.py
```
TRUY CẬP HỆ THỐNG TẠI: **`http://127.0.0.1:8000`**

### 3. Tài Khoản Demo Mặc Định (Mật khẩu: `password123`)
| Tên đăng nhập | Quyền (Role) | Mô tả |
| :--- | :--- | :--- |
| `admin` | **Admin** | Quản trị viên hệ thống |
| `giaovien1` | **Teacher** | ThS. Nguyễn Văn Thắng (CNTT) |
| `giaovien2` | **Teacher** | TS. Trần Thị Hương (Hóa & Sinh) |
| `hocsinh1` | **Student** | Sinh viên Lê Hoàng Nam |
| `hocsinh2` | **Student** | Sinh viên Phạm Mai Anh |

---

## 🗄️ Tầng Dữ Liệu SQL Server (Data Tier)

1. Mở **SQL Server Management Studio (SSMS)** hoặc **Azure Data Studio**.
2. Chạy file script: `sql_server_schema.sql` để khởi tạo Database `ClassroomDB` cùng các bảng `users`, `courses`, `schedules`, `enrollments`, `attendances`, `grades`.
3. Đặt chuỗi kết nối trong biến môi trường (Environment Variable) trước khi chạy app:
   ```bash
   $env:DB_TYPE="sqlserver"
   $env:SQLSERVER_CONN_STR="mssql+pyodbc://sa:MấtKhẩuCủaBạn@localhost:1433/ClassroomDB?driver=ODBC+Driver+17+for+SQL+Server"
   ```
   *(Nếu không cấu hình SQL Server, hệ thống sẽ tự động sử dụng SQLite fallback để ứng dụng chạy ngay mượt mà)*.

---

## 🚀 Hướng Dẫn Push GitHub & Deploy Lên Vercel

### 1. Đẩy Code Lên GitHub Repository
```bash
git add .
git commit -m "Complete 3-Tier Classroom Management System"
git branch -M main
git push -u origin main
```

### 2. Deploy Lên Vercel
1. Truy cập [Vercel Dashboard](https://vercel.com/dashboard) và chọn **"Add New Project"**.
2. Kết nối với GitHub repository: `https://github.com/HuyHago1111/Managerment_of_class.git`.
3. Vercel sẽ tự động nhận diện file `vercel.json` và deploy ứng dụng web của bạn lên Internet!


