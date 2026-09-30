import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database Configuration
# Supports SQL Server (mssql+pyodbc) and fallback to SQLite
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
SQLSERVER_CONN_STR = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "SQLSERVER_CONN_STR",
        "mssql+pyodbc://sa:YourPassword123@localhost:1433/ClassroomDB?driver=ODBC+Driver+17+for+SQL+Server"
    )
)

# On Vercel serverless environment, current directory is read-only, use /tmp directory
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    temp_db_path = os.path.join(tempfile.gettempdir(), "classroom.db")
    default_sqlite_url = f"sqlite:///{temp_db_path}"
else:
    default_sqlite_url = "sqlite:///./classroom.db"

SQLITE_URL = os.getenv("SQLITE_URL", default_sqlite_url)

if DB_TYPE.lower() == "sqlserver":
    try:
        engine = create_engine(
            SQLSERVER_CONN_STR,
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
else:
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    print(f" Using SQLite database engine at {SQLITE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
