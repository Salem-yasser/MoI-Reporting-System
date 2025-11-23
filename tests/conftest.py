import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import urllib.parse

from app.main import app
from app.core.database import get_db_ops, BaseOps
from app.core.config import get_settings

settings = get_settings()

# Test database URL (using Operations DB)
def get_test_database_url() -> str:
    """Get test database URL"""
    conn_str = settings.SQLALCHEMY_DATABASE_URI_OPS
    if "Driver=" not in conn_str:
        conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};{conn_str}"
    params = urllib.parse.quote_plus(conn_str)
    return f"mssql+pyodbc:///?odbc_connect={params}"

TEST_DATABASE_URL = get_test_database_url()

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Test session factory
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a database session for testing"""
    session = TestSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_ops] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()