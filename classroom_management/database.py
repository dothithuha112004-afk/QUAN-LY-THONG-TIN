import os  # Thư viện quản lý hệ thống, biến môi trường và đường dẫn tệp tin
import tempfile  # Thư viện làm việc với thư mục tạm thời của hệ điều hành
from sqlalchemy import create_engine, event  # Hàm khởi tạo engine kết nối cơ sở dữ liệu và lắng nghe sự kiện từ SQLAlchemy
from sqlalchemy.engine import Engine  # Import Engine type cho SQLAlchemy event
from sqlalchemy.orm import declarative_base, sessionmaker  # Lớp cơ sở ánh xạ ORM và lớp tạo phiên làm việc Session

# Database Configuration (Cấu hình cơ sở dữ liệu)
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # Đọc loại CSDL từ biến môi trường DB_TYPE
DATABASE_URL = os.getenv("DATABASE_URL")  # Đọc chuỗi kết nối CSDL Cloud (Supabase, Neon, Postgres, SQL Server)

# Xử lý môi trường Vercel/Serverless: Thư mục hiện tại chỉ đọc (read-only), phải lưu file sqlite vào thư mục tạm /tmp
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):  # Kiểm tra xem app có đang chạy trên đám mây Vercel/Lambda không
    temp_db_path = os.path.join(tempfile.gettempdir(), "classroom.db")  # Đặt đường dẫn file CSDL tạm tại thư mục /tmp
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_db_path = os.path.join(BASE_DIR, "classroom.db")
    if not os.path.exists(temp_db_path) and os.path.exists(repo_db_path):
        import shutil
        try:
            shutil.copy2(repo_db_path, temp_db_path)
        except Exception:
            pass
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

# Khởi tạo Engine kết nối: Ưu tiên DATABASE_URL (Cloud DB như Supabase/Neon/SQLServer), nếu không có thì dùng SQLite
if DATABASE_URL:
    # Chuẩn hóa tiền tố postgres:// thành postgresql:// cho chuẩn SQLAlchemy 2.x
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        with engine.connect() as conn:
            pass
        print(" Connected to Remote Database (DATABASE_URL) successfully!")
    except Exception as e:
        print(f" Warning: Could not connect to DATABASE_URL ({e}). Falling back to SQLite database...")
        engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
elif DB_TYPE.lower() in ["sqlserver", "mssql"]:
    sqlserver_conn_str = os.getenv("SQLSERVER_CONN_STR", "mssql+pyodbc://sa:YourPassword123@localhost:1433/ClassroomDB?driver=ODBC+Driver+17+for+SQL+Server")
    try:
        engine = create_engine(
            sqlserver_conn_str,
            fast_executemany=True,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        with engine.connect() as conn:
            pass
        print(" Connected to Microsoft SQL Server successfully!")
    except Exception as e:
        print(f" Warning: Could not connect to SQL Server ({e}). Falling back to SQLite database...")
        engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
else:  # Mặc định dùng SQLite local/temp
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    try:
        print(f" Using SQLite database engine at: {SQLITE_URL}")
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


