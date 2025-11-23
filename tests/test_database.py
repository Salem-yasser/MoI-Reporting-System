import pytest
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.user import User
from app.models.attachment import Attachment

def test_database_connection(db_session: Session):
    """Test that database connection works"""
    result = db_session.execute("SELECT 1 AS test")
    assert result.scalar() == 1
    print("✓ Database connection working")

def test_create_user(db_session: Session):
    """Test creating a user in the database"""
    user = User(
        userId="test-user-123",
        isAnonymous=False,
        role="citizen",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    
    # Verify user was created
    found_user = db_session.query(User).filter(User.userId == "test-user-123").first()
    assert found_user is not None
    assert found_user.email == "test@example.com"
    print("✓ User creation working")
    
    # Cleanup
    db_session.delete(found_user)
    db_session.commit()

def test_create_report_with_user(db_session: Session):
    """Test creating a report linked to a user"""
    # Create user first
    user = User(
        userId="test-user-456",
        isAnonymous=False,
        role="citizen",
        email="reporter@example.com"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create report
    report = Report(
        reportId="test-report-789",
        title="Test Report",
        descriptionText="This is a test report description",
        locationRaw="Test Location",
        categoryId="infrastructure",
        status="Submitted",
        userId="test-user-456"
    )
    db_session.add(report)
    db_session.commit()
    
    # Verify
    found_report = db_session.query(Report).filter(Report.reportId == "test-report-789").first()
    assert found_report is not None
    assert found_report.userId == "test-user-456"
    assert found_report.user.email == "reporter@example.com"
    print("✓ Report-User relationship working")
    
    # Cleanup
    db_session.delete(found_report)
    db_session.delete(user)
    db_session.commit()