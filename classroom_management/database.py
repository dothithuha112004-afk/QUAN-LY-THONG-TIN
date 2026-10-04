import os  # Thư viện quản lý hệ thống, biến môi trường và đường dẫn tệp tin
import tempfile  # Thư viện làm việc với thư mục tạm thời của hệ điều hành
from sqlalchemy import create_engine, event  # Hàm khởi tạo engine kết nối cơ sở dữ liệu và lắng nghe sự kiện từ SQLAlchemy
from sqlalchemy.engine import Engine  # Import Engine type cho SQLAlchemy event
from sqlalchemy.orm import declarative_base, sessionmaker  # Lớp cơ sở ánh xạ ORM và lớp tạo phiên làm việc Session

# Database Configuration (Cấu hình cơ sở dữ liệu)
# Hỗ trợ kết nối Microsoft SQL Server (mssql+pyodbc) và cơ chế tự động chuyển sang SQLite (Fallback)
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # Đọc loại CSDL từ biến môi trường DB_TYPE, mặc định là "sqlite"
SQLSERVER_CONN_STR = os.getenv(  # Đọc chuỗi kết nối SQL Server từ biến môi trường
    "DATABASE_URL",
    os.getenv(
        "SQLSERVER_CONN_STR",
        "mssql+pyodbc://sa:YourPassword123@localhost:1433/ClassroomDB?driver=ODBC+Driver+17+for+SQL+Server"  # Chuỗi kết nối mặc định tới SQL Server local
    )
)

# Xử lý môi trường Vercel/Serverless: Thư mục hiện tại chỉ đọc (read-only), phải lưu file sqlite vào thư mục tạm /tmp
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):  # Kiểm tra xem app có đang chạy trên đám mây Vercel/Lambda không
    temp_db_path = os.path.join(tempfile.gettempdir(), "classroom.db")  # Đặt đường dẫn file CSDL tạm tại thư mục /tmp
    default_sqlite_url = f"sqlite:///{temp_db_path}"  # Tạo URL kết nối SQLite cho môi trường tạm
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_file_path = os.path.join(BASE_DIR, "classroom.db")
    default_sqlite_url = f"sqlite:///{db_file_path}"  # Tạo URL kết nối SQLite tuyệt đối tới file classroom.db

SQLITE_URL = os.getenv("SQLITE_URL", default_sqlite_url)  # Lấy URL kết nối SQLite chính thức

# Cấu hình WAL (Write-Ahead Logging) cho SQLite để phần mềm Letos và Web đọc/ghi đồng thời không bị khoá (db locked)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Bật WAL mode cho SQLite giúp Letos GUI và FastAPI đồng bộ dữ liệu tức thì."""
    if "sqlite" in str(dbapi_connection.__class__).lower() or hasattr(dbapi_connection, "cursor"):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.close()
        except Exception:
            pass

if DB_TYPE.lower() == "sqlserver":  # Nếu người dùng cấu hình chọn loại CSDL là SQL Server
    try:
        engine = create_engine(  # Khởi tạo engine kết nối SQL Server
            SQLSERVER_CONN_STR,  # Truyền chuỗi kết nối SQL Server
            fast_executemany=True,  # Tăng tốc độ ghi dữ liệu nhiều dòng đồng thời cho SQL Server
            pool_pre_ping=True,  # Tự động kiểm tra kết nối còn sống hay không trước khi gửi truy vấn
            pool_recycle=3600  # Tự động làm mới kết nối sau mỗi 1 giờ (3600 giây)
        )
        with engine.connect() as conn:  # Thử thực hiện kết nối thực tế tới SQL Server
            pass  # Nếu kết nối thành công thì bỏ qua
        print(" Connected to Microsoft SQL Server successfully!")  # In thông báo kết nối SQL Server thành công
    except Exception as e:  # Nếu gặp lỗi không kết lỗi được SQL Server
        print(f" Warning: Could not connect to SQL Server ({e}). Falling back to SQLite database...")  # In cảnh báo lỗi
        engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})  # Tự động chuyển (fallback) sang dùng SQLite
else:  # Nếu cấu hình mặc định dùng SQLite
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})  # Khởi tạo engine kết nối SQLite (cho phép đa luồng)
    try:
        print(f" Using SQLite database engine at: {SQLITE_URL}")  # In thông báo đang sử dụng SQLite
    except Exception:
        print(" Using SQLite database engine.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Khởi tạo class tạo phiên làm việc Session kết nối với engine
Base = declarative_base()  # Tạo lớp cơ sở Base để các Model dữ liệu ORM kế thừa

def get_db():  # Hàm Dependency trong FastAPI cung cấp Session làm việc với CSDL cho mỗi API request
    """Dependency for DB session."""
    db = SessionLocal()  # Khởi tạo một phiên làm việc (session) CSDL mới
    try:
        yield db  # Trả phiên làm việc db cho hàm API sử dụng
    finally:
        db.close()  # Đảm bảo đóng phiên làm việc db sau khi API xử lý xong để giải phóng tài nguyên


