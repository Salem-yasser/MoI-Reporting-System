import pytest
from fastapi.testclient import TestClient

def test_create_report(client: TestClient):
    """Test creating a new report"""
    payload = {
        "title": "Test Pothole",
        "descriptionText": "This is a test pothole report for testing purposes",
        "categoryId": "infrastructure",
        "location": "King Faisal Street, Giza",
        "isAnonymous": False,
        "attachments": []
    }

    response = client.post("/api/v1/reports/", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    assert data["title"] == "Test Pothole"
    assert data["status"] == "Submitted"
    assert "reportId" in data
    
    print(f"✓ Created report: {data['reportId']}")
    return data["reportId"]

def test_list_reports(client: TestClient):
    """Test listing reports"""
    # Create a report first
    create_response = client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for List",
            "descriptionText": "Test description for listing",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # List reports
    response = client.get("/api/v1/reports/?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "reports" in data
    assert "total" in data
    assert isinstance(data["reports"], list)
    assert len(data["reports"]) > 0
    
    # Verify structure
    found = False
    for report in data["reports"]:
        assert "reportId" in report
        assert "categoryId" in report
        assert "location" in report
        if report["reportId"] == report_id:
            found = True
    
    assert found, f"Created report {report_id} not found in list"
    print(f"✓ Listed {len(data['reports'])} reports")

def test_get_report(client: TestClient):
    """Test getting a specific report"""
    # Create a report first
    create_response = client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for Get",
            "descriptionText": "Test description for getting",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # Get the report
    response = client.get(f"/api/v1/reports/{report_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["reportId"] == report_id
    assert data["title"] == "Test Report for Get"
    
    print(f"✓ Retrieved report: {report_id}")

def test_update_report_status(client: TestClient):
    """Test updating report status"""
    # Create a report first
    create_response = client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for Update",
            "descriptionText": "Test description for updating",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # Update status
    payload = {
        "status": "Assigned",
        "notes": "Assigned to maintenance team"
    }
    
    response = client.put(
        f"/api/v1/reports/{report_id}/status",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Assigned"
    assert data["reportId"] == report_id
    
    # Verify the change persisted
    check_response = client.get(f"/api/v1/reports/{report_id}")
    check_data = check_response.json()
    assert check_data["status"] == "Assigned"
    
    print(f"✓ Updated report status: {report_id}")

def test_delete_report(client: TestClient):
    """Test deleting a report"""
    # Create a report first
    create_response = client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for Delete",
            "descriptionText": "Test description for deleting",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # Delete the report
    response = client.delete(f"/api/v1/reports/{report_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/reports/{report_id}")
    assert get_response.status_code == 404
    
    print(f"✓ Deleted report: {report_id}")

def test_filter_by_status(client: TestClient):
    """Test filtering reports by status"""
    # Create reports with different statuses
    report1 = client.post(
        "/api/v1/reports/",
        json={
            "title": "Submitted Report",
            "descriptionText": "This should be in Submitted status",
            "categoryId": "infrastructure",
            "location": "Location A",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert report1.status_code == 201
    
    # List only Submitted reports
    response = client.get("/api/v1/reports/?status=Submitted")
    
    assert response.status_code == 200
    data = response.json()
    assert all(r["status"] == "Submitted" for r in data["reports"])
    print(f"✓ Filtered {len(data['reports'])} Submitted reports")

def test_filter_by_category(client: TestClient):
    """Test filtering reports by category"""
    # Create report
    client.post(
        "/api/v1/reports/",
        json={
            "title": "Infrastructure Issue",
            "descriptionText": "Road needs repair",
            "categoryId": "infrastructure",
            "location": "Main Street",
            "isAnonymous": False,
            "attachments": []
        }
    )
    
    # Filter by category
    response = client.get("/api/v1/reports/?category=infrastructure")
    
    assert response.status_code == 200
    data = response.json()
    assert all(r["categoryId"] == "infrastructure" for r in data["reports"])
    print(f"✓ Filtered {len(data['reports'])} infrastructure reports")

def test_pagination(client: TestClient):
    """Test pagination works correctly"""
    # Create multiple reports
    for i in range(5):
        client.post(
            "/api/v1/reports/",
            json={
                "title": f"Pagination Test {i}",
                "descriptionText": f"Testing pagination report {i}",
                "categoryId": "infrastructure",
                "location": f"Location {i}",
                "isAnonymous": False,
                "attachments": []
            }
        )
    
    # Get first page (2 items)
    page1 = client.get("/api/v1/reports/?skip=0&limit=2")
    assert page1.status_code == 200
    data1 = page1.json()
    assert len(data1["reports"]) <= 2
    assert data1["page"] == 1
    
    # Get second page
    page2 = client.get("/api/v1/reports/?skip=2&limit=2")
    assert page2.status_code == 200
    data2 = page2.json()
    assert len(data2["reports"]) <= 2
    assert data2["page"] == 2
    
    print("✓ Pagination working correctly")

def test_invalid_report_creation(client: TestClient):
    """Test validation errors"""
    # Missing required field
    invalid_payload = {
        "title": "AB",  # Too short
        "descriptionText": "Short",  # Too short
        "categoryId": "infrastructure",
        "location": "Test"
    }
    
    response = client.post("/api/v1/reports/", json=invalid_payload)
    assert response.status_code == 422  # Validation error
    print("✓ Validation working correctly")

def test_get_nonexistent_report(client: TestClient):
    """Test getting a report that doesn't exist"""
    response = client.get("/api/v1/reports/nonexistent-id-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    print("✓ 404 handling working correctly")