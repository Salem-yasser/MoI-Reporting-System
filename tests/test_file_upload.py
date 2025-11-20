import pytest
from httpx import AsyncClient
import io

@pytest.mark.asyncio
async def test_upload_attachment(client: AsyncClient):
    """Test uploading a file to a report."""
    # Create a report first
    create_response = await client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report with Files",
            "descriptionText": "Testing file uploads",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # Create a fake image file
    fake_image = io.BytesIO(b"fake image content")
    
    # Upload file
    files = {"files": ("test.jpg", fake_image, "image/jpeg")}
    response = await client.post(
        f"/api/v1/reports/{report_id}/attachments",
        files=files
    )
    
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["fileType"] == "image"
    assert data[0]["reportId"] == report_id
    
    print(f"✓ Uploaded attachment to report: {report_id}")