from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_report():
    """Test creating a new report"""
    response = client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Pothole",
            "descriptionText": "This is a test pothole report for testing purposes",
            "categoryId": "infrastructure",
            "latitude": 30.0444,
            "longitude": 31.2357
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Pothole"
    assert data["status"] == "Submitted"
    assert "reportId" in data
    print(f"✓ Created report: {data['reportId']}")
    
    return data["reportId"]

def test_list_reports():
    """Test listing reports"""
    response = client.get("/api/v1/reports/?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert "total" in data
    print(f"✓ Listed {len(data['reports'])} reports")

def test_get_report():
    """Test getting a specific report"""
    # First create a report
    report_id = test_create_report()
    
    # Then get it
    response = client.get(f"/api/v1/reports/{report_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["reportId"] == report_id
    print(f"✓ Retrieved report: {report_id}")

def test_update_report_status():
    """Test updating report status"""
    report_id = test_create_report()
    
    response = client.put(
        f"/api/v1/reports/{report_id}/status",
        json={
            "status": "Assigned",
            "notes": "Assigned to maintenance team"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Assigned"
    print(f"✓ Updated report status: {report_id}")

if __name__ == "__main__":
    print("🧪 Testing Report API Endpoints...")
    print("=" * 50)
    
    test_create_report()
    test_list_reports()
    test_get_report()
    test_update_report_status()
    
    print("=" * 50)
    print("✅ All tests passed!")
