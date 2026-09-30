import os  # Thư viện hệ điều hành: dùng để xử lý đường dẫn file, thư mục
from fastapi import FastAPI  # Import class FastAPI để khởi tạo ứng dụng web API
from fastapi.staticfiles import StaticFiles  # Dùng để phục vụ file tĩnh (CSS, JavaScript, hình ảnh)
from fastapi.responses import HTMLResponse  # Định dạng phản hồi trả về là mã HTML
from classroom_management.database import engine, Base  # Import kết nối DB (engine) và lớp cơ sở ánh xạ ORM (Base)
from classroom_management.seed import seed_database  # Import hàm tạo dữ liệu mẫu ban đầu (admin, giáo viên, sinh viên mẫu)
from classroom_management.routers import auth_router, admin_router, teacher_router, student_router  # Import các router phân hệ tính năng

# ================= KHỞI TẠO CƠ SỞ DỮ LIỆU & DỮ LIỆU MẪU =================
Base.metadata.create_all(bind=engine)  # Tự động tạo tất cả các bảng trong DB (nếu chưa tồn tại) theo cấu hình models
try:
    seed_database()  # Gọi hàm thêm dữ liệu mẫu vào DB khi chạy lần đầu
except Exception as e:
    print(f"Seed info: {e}")  # Nếu dữ liệu đã tồn tại hoặc có lỗi thì in thông báo ra terminal mà không làm dừng ứng dụng

# ================= HÀM FACTORY TẠO VÀ CẤU HÌNH APP FASTAPI =================
def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    # Khởi tạo đối tượng ứng dụng FastAPI kèm thông tin metadata hiển thị trên trang Swagger (/docs)
    app = FastAPI(
        title="Hệ Thống Quản Lý Lớp Học - Enterprise Python",
        description="Dự án Python 3 tầng Quản lý lớp học phân quyền Giáo viên, Sinh viên, Admin",
        version="1.0.0"
    )

    # 1. Đăng ký các Router quản lý từng phân hệ (Authentication, Admin, Teacher, Student)
    app.include_router(auth_router.router)      # Router xử lý Đăng nhập / Đăng xuất / Lấy thông tin user
    app.include_router(admin_router.router)     # Router quản lý phân quyền Admin (QL Môn học, Lớp học, Tài khoản)
    app.include_router(teacher_router.router)   # Router phân hệ Giáo viên (Điểm danh, Nhập điểm, Tạo bài tập)
    app.include_router(student_router.router)   # Router phân hệ Sinh viên (Xem lịch, Xem điểm, Nộp bài)

    # 2. Cấu hình thư mục chứa file tĩnh (CSS / JS / Assets)
    static_dir = os.path.join(os.path.dirname(__file__), "static")  # Lấy đường dẫn tuyệt đối đến thư mục 'static'
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")  # Mount đường dẫn /static vào app

    # 3. Route trang chủ (Root URL: "/")
    @app.get("/", response_class=HTMLResponse)  # Bắt sự kiện GET request vào đường dẫn gốc "/"
    def read_root():
        """Render single page dashboard interface."""
        index_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")  # Tìm file giao diện index.html
        with open(index_path, "r", encoding="utf-8") as f:  # Đọc nội dung file HTML với mã hóa UTF-8
            content = f.read()
        return HTMLResponse(content=content)  # Trả về toàn bộ giao diện HTML cho trình duyệt

    return app  # Trả về đối tượng ứng dụng đã cấu hình hoàn chỉnh

# ================= KHỞI TẠO BIẾN APP CHO ASGI SERVER (UVICORN) CHẠY =================
app = create_app()  # Tạo instance app chính thức để Uvicorn gọi chạy (ví dụ: uvicorn classroom_management.main:app)
